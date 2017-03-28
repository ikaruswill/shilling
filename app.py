from flask import Flask, jsonify, make_response, request

import os
import json
import logging
import requests

logging.basicConfig(filename='app.log',level=logging.DEBUG)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    logging.debug('/ GET')
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.challenge'):
        if not request.args.get('hub.verify_token') == os.environ['VERIFY_TOKEN']:
            return 'Token Mismatch', 403

    return request.args['hub.challenge'], 200

@app.route('/', methods=['POST'])
def webhook():
    logging.debug('/ POST')
    data = request.get_json()

    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                # receive a message
                if messaging_event.get('message'):

                    sender_id = messaging_event['sender']['id'] # sender facebook ID
                    recipient_id = messaging_event['recipient']['id']  # our page ID
                    message_text = messaging_event['message']['text']
                    logging.debug('received message ' + message_text)
                    send_message(sender_id, 'RECEIVED')

                if messaging_event.get('delivery'):  # delivery confirmation
                    pass

                if messaging_event.get('optin'):  # optin confirmation
                    pass

                if messaging_event.get('postback'):  # user clicked/tapped 'postback' button in earlier message
                    pass

    return 'ok', 200

@app.route('/summary', methods=['GET'])
def get_summary():
    user_id = request.args.get('userId')
    if not user_id:
        return 'Missing User ID', 403
    return 'SUMMARY IN RETURN', 200

def send_message(recipient_id, message_text):

    params = {
        'access_token': os.environ['PAGE_ACCESS_TOKEN']
    }
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text
        }
    })
    r = requests.post('https://graph.facebook.com/v2.6/me/messages', params=params, headers=headers, data=data)
    if r.status_code != 200:
        print('fail to send message')
        print(r.status_code)
        print(r.text)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
