import json
import logging
import os
from libraries.df_response_lib import *

from flask import Flask,request, make_response, jsonify
from google.cloud import firestore

app = Flask(__name__)
log = app.logger

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = None
    logging.info('Request: ' + json.dumps(req, indent=4))

    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'


    if action == 'get.session.status':
        aog = actions_on_google_response()
        fulfillmentText, current_content, current_meaning = sessionStatus(req)

        aog_sr = aog.simple_response([
            [fulfillmentText, fulfillmentText, False]
        ])

        aog_additional_resp = aog.simple_response([
            ["Here a small story for you. " + current_content.get(u'paragraphs').get(u'para_1'),
             "Here a small story for you. " + current_content.get(u'paragraphs').get(u'para_1'), False]
        ])
        basic_card = aog.basic_card(current_content.get(u'title') ,
                                    current_meaning.get(u'title'),
                                    current_content.get(u'paragraphs').get(u'para_1'),
                                    # current_meaning.get(u'paragraphs').get(u'para_1').get(u'meaning_1'),
                                    image=[current_content.get(u'images'), current_content.get(u'title')])

        ff_response = fulfillment_response()
        ff_text = ff_response.fulfillment_text(fulfillmentText)
        ff_messages = ff_response.fulfillment_messages([aog_sr, basic_card, aog_additional_resp])

        reply = ff_response.main_response(ff_text, ff_messages)


    elif action == 'meaning.after.all':
        aog = actions_on_google_response()
        fulfillmentText, current_content, current_meaning = sessionStatus(req)

        aog_sr = aog.simple_response([
            [fulfillmentText, fulfillmentText, False]
        ])

        aog_additional_resp = aog.simple_response([
            ["Here a small story for you. " + current_content.get(u'paragraphs').get(u'para_1'),
             "Here a small story for you. " + current_content.get(u'paragraphs').get(u'para_1'), False]
        ])

        aog_additional_resp_2 = aog.simple_response([
            ["Do you know the meaning of " + current_meaning.get(u'title'),
             "Do you know the meaning of " + current_meaning.get(u'title'), False]
        ])

        # aog_sc = aog.suggestion_chips(current_content.get(u'items'))
        # list_title, list_arr = get_content_list(current_content, current_meaning)
        # list_select = aog.build_list_select(list_title, list_arr)

        basic_card = aog.basic_card(current_content.get(u'title'),
                                    current_meaning.get(u'title'),
                                    current_content.get(u'paragraphs').get(u'para_1'),
                                    # current_meaning.get(u'paragraphs').get(u'para_1').get(u'meaning_1'),
                                    image=[current_content.get(u'images'), current_content.get(u'title')])

        ff_response = fulfillment_response()
        ff_text = ff_response.fulfillment_text(fulfillmentText)
        ff_messages = ff_response.fulfillment_messages([aog_sr, basic_card, aog_additional_resp])

        reply = ff_response.main_response(ff_text, ff_messages)

        logging.info('meaning.after.all')
    else:
        logging.error('Unexpected action.')
    return make_response(jsonify(reply))



def sessionStatus(req):
    logging.info(req.get('queryResult').get('parameters'))

    result = req.get('queryResult')
    parameters = result.get('parameters')
    user = parameters.get('user-name')

    try:
        if not firebase_admin._apps:
            db = setup_client()
        db = firestore.client()
        is_session_started, first_name = lookup_users(db, user)
    except Exception as e:
        logging.info(e)
        exit(1)

    if is_session_started == True:
        speech = 'Ok ' + first_name + ', here is the latest idioms we are going to discuss in this session.'
        current_content, current_meaning = get_content(db,user)
        update_learning_for_user(db, user)

    elif is_session_started == False:
        speech = 'Ok ' + first_name + ', let me explain the objective, teaching and assessment methods.'
        current_content, current_meaning = get_intro_content(db, user)
    else:
        speech = 'User ' + first_name + ' is not registered. Please register yourself, before starting this tutorials.'

    logging.info('Response: %s', speech)
    return speech, current_content, current_meaning

def update_learning_for_user(db, user):

    return ""

def get_intro_content(db, user):
    return ""

def get_content_list(current_content, current_meaning):

    list_title = current_content.get(u'title')

    list_arr = [
        [current_meaning.get(u'title'), current_meaning.get(u'paragraphs').get(u'para_1').get(u'meaning_1'),
         [current_meaning.get(u'title'),[current_meaning.get(u'title')]],
         [current_content.get(u'images'), current_content.get(u'title')]],
        [current_meaning.get(u'title'), current_meaning.get(u'paragraphs').get(u'para_2').get(u'meaning_1'),
         [current_meaning.get(u'title'), [current_meaning.get(u'title')]],
         [current_content.get(u'images'), current_content.get(u'title')]]
    ]

    return list_title, list_arr

def get_content(db, user):
    learning = (db.collection(u'learnings').document(user).get()).to_dict()

    content_dict = db.document(learning.get(u'current_studying_content').get(u'content_id').path).get().to_dict()
    meaning_dict = db.document(learning.get(u'current_studying_meaning').get('meaning_id').path).get().to_dict()

    return content_dict, meaning_dict

def lookup_users(db, user):
    user_ref = (db.collection(u'users').document(user)).get()
    result = user_ref.to_dict()

    return result.get(u'session_started'), result.get(u'first_name')


def setup_client():
    prject_id = os.environ.get('PROJECT_ID')
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': prject_id,
    })

    return firestore.client()

def generate_uuid(doc_ref, id_col):
    return doc_ref.update({ id_col : firestore.Increment(1)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' , port=8000)
