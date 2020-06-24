import json
import os

from flask import Flask, request, make_response, jsonify
from google.cloud import firestore

from libraries.df_response_lib import *
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
log = app.logger

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from learnings import Learning


def setup_client():
    prject_id = os.environ.get('PROJECT_ID')
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': prject_id,
    })
    return firestore.client()


try:
    if not firebase_admin._apps:
        db = setup_client()
    db = firestore.client()
except Exception as e:
    log.info(e)
    exit(1)


@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    reply = {}
    log.debug('Request: ' + json.dumps(req, indent=4))

    try:
        log.debug(req.get('queryResult').get('parameters'))
        action = req.get('queryResult').get('action')
        user = req.get('queryResult').get('parameters').get('user-name')

        if action == 'get.session.status':
            reply = session_status(user)
            log.debug(json.dumps(reply, indent=4))
        elif action == 'get.after.all.content':
            idiom = req.get('queryResult').get('parameters').get('idioms')
            reply = build_meaning_card(idiom, user)
            log.debug(json.dumps(reply, indent=4))
        elif action == 'get.crocodile.tears.content':
            idiom = req.get('queryResult').get('parameters').get('idioms')
            reply = build_meaning_card(idiom, user)
            log.debug(json.dumps(reply, indent=4))
        else:
            log.error('Unexpected action.')
    except AttributeError:
        log.error('json error')
        return 'json error'
    except Exception as e:
        log.error(e)
        return e

    return make_response(jsonify(reply))


def build_content_list(user):
    """

    :param idiom:
    :return:
    """
    current_content, current_meaning = get_content_for_user(user)
    meaning_list = get_meaning_list(current_content.get(u'content_id'))
    aog = actions_on_google_response()

    messag = f"Please go ahead and select the idiom you want to study."

    aog_sr = aog.simple_response([
        [messag, messag, False]
    ])

    list_arr = []
    for meaning in meaning_list:
        list_arr.append([meaning.get(u'title'), meaning.get(u'explanation').get(u'meaning'),
                         [meaning.get(u'title'), [meaning.get(u'title')]],
                         [meaning.get(u'image_url'), meaning.get(u'title')]])

    list_select = aog.list_select(current_content[u'title'], list_arr)

    ff_response = fulfillment_response()
    ff_text = ff_response.fulfillment_text(messag)
    ff_messages = ff_response.fulfillment_messages([aog_sr, list_select])

    reply = ff_response.main_response(ff_text, ff_messages)

    return reply


def build_meaning_card(idiom,user=None):
    """
    buid card response with list for showing idiom meaning
    :param idiom: idiom title for serching from mening collection
    :param user: user name from dialogflow optional till now
    :return: response in the formate simple response & basic card
    """

    aog = actions_on_google_response()
    current_meaning = get_meaning_card(idiom)

    message = f" {current_meaning.get(u'title')} means {current_meaning.get(u'explanation').get(u'meaning')}. \r\n"
    if current_meaning.get(u'explanation').get(u'examples') != "":
        message += f"For example {current_meaning.get(u'explanation').get(u'examples')}.\r\n"
    if current_meaning.get(u'explanation').get(u'origin'):
        message += f"Origin: {current_meaning.get(u'explanation').get(u'origin')}. \r\n"


    aog_sr = aog.simple_response([[message, message, False]])

    basic_card = aog.basic_card(current_meaning.get(u'title'),
                                current_meaning.get(u'sub_title'),
                                message,
                                image=[current_meaning.get(u'image_url'), current_meaning.get(u'title')])

    ff_response = fulfillment_response()
    ff_text = ff_response.fulfillment_text(aog_sr)
    ff_messages = ff_response.fulfillment_messages([aog_sr, basic_card])
    reply = ff_response.main_response(ff_text, ff_messages)
    # update_learning_for_user(user, current_content[u'content_id'], current_meaning[u'meaning_id'])
    log.debug(json.dumps(reply, indent=4))
    return reply


def session_status(user):
    """
    Set the session for the user and fetch user info from db
    :param user:
    :return: action on google response object
    """
    is_session_started, first_name = lookup_users(db, user)

    if is_session_started == True:
        speech = 'Ok ' + first_name + ', here is the latest idioms we are going to discuss in this session.'
        current_content, current_meaning = get_content_for_user(user)
        reply = get_content_list(speech, current_content, current_meaning,
                                 get_meaning_list(current_content[u'content_id']))
    elif is_session_started == False:
        speech = 'Ok ' + first_name + ', let me explain the objective, teaching and assessment methods.'
        onboarding_user(user)
        current_content, current_meaning = get_content_for_user(user)
        reply = get_content_list(current_content, current_meaning)
    else:
        speech = 'User ' + first_name + ' is not registered. Please register yourself, before starting this tutorials.'
        aog = actions_on_google_response()
        aog_sr = aog.simple_response([
            [speech, speech, False]
        ])
        ff_response = fulfillment_response()
        ff_text = ff_response.fulfillment_text(speech)
        ff_messages = ff_response.fulfillment_messages([aog_sr])

        reply = ff_response.main_response(ff_text, ff_messages)

    log.debug(json.dumps(speech, indent=4))
    return reply


def onboarding_user(user):
    """
    Setting the learning records for a user
    :param user:
    :return: return True if created a document in learing connection
    """
    try:
        content, meaning = get_content_for_user(user)
        db.collection(u'learnings').document(user).update(
            Learning(user=user,
                     content_id=db.document(content[u'content_id']),
                     last_content_watched_on=firestore.SERVER_TIMESTAMP,
                     # content_para_1=True,
                     last_meaning_watched_on=firestore.SERVER_TIMESTAMP,
                     meaning_id=db.document(meaning[u'meaning_id'])
                     ).to_dict())
    except Exception as e:
        log.error(e)
        return False

    return True


def update_learning_for_user(user, content_id, meaning_id):
    """
    Update learing status for a user
    :param user: user-name parameter as received from intent request
    :param content_id: id for the content currently read by the user
    :param meaning_id: id for the meaning currently read by the user
    :return:
    """
    try:
        db.collection(u'learnings').document(user).update(
            Learning(user=user,
                     content_id=db.document(content_id),
                     last_content_watched_on=firestore.SERVER_TIMESTAMP,
                     # content_para_1=True,
                     last_meaning_watched_on=firestore.SERVER_TIMESTAMP,
                     meaning_id=db.document(meaning_id)
                     ).to_dict())
    except Exception as e:
        log.error(e)
        exit(1)

    return 1


def get_intro_content(db, user):
    return ""


def get_content_for_user(user):
    """
    Get current content & meaning in dict for the user
    :param user: user-name parameter as received from intent request
    :return: Content dictionary , Meaning dictionary
    """
    learning = (db.collection(u'learnings').document(user).get()).to_dict()
    content_dict = db.document(learning.get(u'current_studying_content').get(u'content_id').path).get().to_dict()
    meaning_dict = db.document(learning.get(u'current_studying_meaning').get('meaning_id').path).get().to_dict()
    content_dict[u'content_id'] = learning.get(u'current_studying_content').get(u'content_id').path
    meaning_dict[u'meaning_id'] = learning.get(u'current_studying_meaning').get('meaning_id').path
    return content_dict, meaning_dict


def get_meaning_card(meaning_title):
    """
    Get card response for a content using meaning title
    :param meaning_title:
    :return:
    """
    meaning_dict = {}
    contents = db.collection_group(u'meaning').where(u'title', u'==', meaning_title).stream()
    for contet in contents:
        meaning_dict = contet.to_dict()

    return meaning_dict


def get_meaning_list(content_id):
    """
    Get list of meaning for a content id
    :param user:
    :return: list of Meaning dictionary
    """
    meaning_dict_list = []
    meanings = db.document(content_id).collection(u'meaning').stream()
    for meaning in meanings:
        meaning_dict_list.append(meaning.to_dict())

    return meaning_dict_list


def lookup_users(db, user):
    user_ref = (db.collection(u'users').document(user)).get()
    result = user_ref.to_dict()

    return result.get(u'session_started'), result.get(u'first_name')


def get_content_list(fulfillment_text, current_content, current_meaning, meaning_list):
    """
     Build List from content
    :param fulfillment_text:
    :param current_content:
    :param current_meaning:
    :param meaning_list:
    :return:
    """

    aog = actions_on_google_response()

    messag = f"{fulfillment_text}. We will start with a short story, {current_content.get(u'sub_title')}. \n\r " \
             f"{current_content.get(u'paragraphs').get(u'para_1')} \n\r " \
             f"{current_content.get(u'paragraphs').get(u'para_4')} \n\r " \
             f"Please go ahead and select the idiom you want to study."

    aog_sr = aog.simple_response([
        [messag, messag, False]
    ])

    list_arr = []

    for meaning in meaning_list:
        list_arr.append([meaning.get(u'title'), meaning.get(u'explanation').get(u'meaning'),
                         [meaning.get(u'title'), [meaning.get(u'title')]],
                         [meaning.get(u'image_url'), meaning.get(u'title')]])

    list_select = aog.list_select(current_content[u'title'], list_arr)

    ff_response = fulfillment_response()
    ff_text = ff_response.fulfillment_text(fulfillment_text)
    ff_messages = ff_response.fulfillment_messages([aog_sr, list_select])

    reply = ff_response.main_response(ff_text, ff_messages)

    return reply


def generate_uuid(doc_ref, id_col):
    return doc_ref.update({id_col: firestore.Increment(1)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
