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
        action = req.get('queryResult').get('action')

        if action == 'get.session.status':
            aog = actions_on_google_response()
            fulfillment_text = session_status(req)

            aog_sr = aog.simple_response([
                [fulfillment_text, fulfillment_text, False]
            ])

            ff_response = fulfillment_response()
            ff_text = ff_response.fulfillment_text(fulfillment_text)
            ff_messages = ff_response.fulfillment_messages([aog_sr])

            reply = ff_response.main_response(ff_text, ff_messages)
            log.debug(json.dumps(reply, indent=4))

        elif action == 'get.after.all.content':

            log.debug(req.get('queryResult').get('parameters'))
            user = req.get('queryResult').get('parameters').get('user-name')

            reply = build_response_content(user)
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


def build_response_content(user):
    """
    buid response for the user request
    :param user: user name from dialogflow
    :return: response in the formate simple response & basic card
    """

    aog = actions_on_google_response()
    current_content, current_meaning = get_content_for_user(user)

    aog_sr = aog.simple_response([
        ["Here a small story for you. " + current_content.get(u'paragraphs').get(u'para_1'),
         "Here a small story for you. " + current_content.get(u'paragraphs').get(u'para_1'), True]
    ])
    basic_card = aog.basic_card(current_content.get(u'title'),
                                current_meaning.get(u'title'),
                                current_meaning.get(u'paragraphs').get(u'para_1').get(u'meaning_1'),
                                image=[current_content.get(u'images'), current_content.get(u'title')])

    ff_response = fulfillment_response()
    ff_text = ff_response.fulfillment_text(aog_sr)
    ff_messages = ff_response.fulfillment_messages([aog_sr, basic_card])
    reply = ff_response.main_response(ff_text, ff_messages)
    update_learning_for_user(user, current_content[u'content_id'], current_meaning[u'meaning_id'])
    log.debug(json.dumps(reply, indent=4))
    return reply


def session_status(req):
    """
    Set the session for the user and fetch user info from db
    :param req: request receive from dialogflow
    :return: simple response in text
    """

    log.debug(req.get('queryResult').get('parameters'))

    user = req.get('queryResult').get('parameters').get('user-name')

    is_session_started, first_name = lookup_users(db, user)

    if is_session_started == True:
        speech = 'Ok ' + first_name + ', here is the latest idioms we are going to discuss in this session.'
    elif is_session_started == False:
        speech = 'Ok ' + first_name + ', let me explain the objective, teaching and assessment methods.'
    else:
        speech = 'User ' + first_name + ' is not registered. Please register yourself, before starting this tutorials.'

    log.debug(json.dumps(speech, indent=4))
    return speech


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
                     content_para_1=True,
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


def lookup_users(db, user):
    user_ref = (db.collection(u'users').document(user)).get()
    result = user_ref.to_dict()

    return result.get(u'session_started'), result.get(u'first_name')


def get_content_list(current_content, current_meaning):
    list_title = current_content.get(u'title')

    list_arr = [
        [current_meaning.get(u'title'), current_meaning.get(u'paragraphs').get(u'para_1').get(u'meaning_1'),
         [current_meaning.get(u'title'), [current_meaning.get(u'title')]],
         [current_content.get(u'images'), current_content.get(u'title')]],
        [current_meaning.get(u'title'), current_meaning.get(u'paragraphs').get(u'para_2').get(u'meaning_1'),
         [current_meaning.get(u'title'), [current_meaning.get(u'title')]],
         [current_content.get(u'images'), current_content.get(u'title')]]
    ]

    return list_title, list_arr


def generate_uuid(doc_ref, id_col):
    return doc_ref.update({id_col: firestore.Increment(1)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
