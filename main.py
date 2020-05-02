import json
import logging
import os

from flask import Flask, request, make_response, jsonify
from google.cloud import firestore

app = Flask(__name__)
log = app.logger

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


@app.route('/', methods=['POST'])
def webhook(request):
    req = request.get_json(silent=True, force=True)
    res = None
    logging.info('Request: ' + json.dumps(req, indent=4))

    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    if action == 'get.session.status':
        res = sessionStatus(req)
    else:
        log.error('Unexpected action.')

    print('Action: ' + action)
    print('Response: ' + res)

    return make_response(jsonify({'fulfillmentText': res}))


def sessionStatus(req):
    logging.info(req.get('queryResult').get('parameters'))

    result = req.get('queryResult')
    parameters = result.get('parameters')
    user = parameters.get('user-name')

    # statusConst = {'sourav': True, 'shamik': False}

    # if statusConst[user]:
    #     speech = 'Ok ' + user + ', here is the list of idioms with the last one highlighted and performance of others displayed'
    # else:
    #     speech = 'Let me explain the objective, teaching and assessment methods'

    if lookup_session_status(user):
        speech = 'Ok ' + str(lookup_session_status(user)) + ', here is the list of idioms with the last one highlighted and performance of others displayed'
    else:
        speech = 'Let me explain the objective, teaching and assessment methods'

    logging.info('Response: %s', speech)

    return speech

def lookup_session_status(user):
    if not firebase_admin._apps:
        db = setup_client()

    db = firestore.client()
    docs = db.collection(u'users').where(u'first_name', u'==', user).stream()
    result = {}
    for doc in docs:
        result = doc.to_dict()

    return result.get('session_started')


def setup_client():
    prject_id = os.environ.get('PROJECT_ID')
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': prject_id,
    })

    return firestore.client()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
