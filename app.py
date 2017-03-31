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
                print(messaging_event)

                if messaging_event.get('message'): # receive a message
                    handle_message(messaging_event)

                if messaging_event.get('delivery'):  # delivery confirmation
                    pass

                if messaging_event.get('optin'):  # optin confirmation
                    pass

                if messaging_event.get('postback'):  # user clicked/tapped 'postback' button in earlier message
                    handle_postback(messaging_event)

    return 'ok', 200

@app.route('/summary', methods=['GET'])
def get_summary():
    user_id = request.args.get('userId')
    if not user_id:
        return 'Missing User ID', 403
    return 'SUMMARY IN RETURN', 200

def handle_message(messaging_event):
    sender_id = messaging_event['sender']['id'] # sender facebook ID
    recipient_id = messaging_event['recipient']['id']  # our page ID
    message_text = messaging_event['message']['text']

    logging.debug('received message ' + message_text)
    print('received message', message_text)

    send_typing_action(sender_id)

    if message_text == 'button':
        # EXAMPLE OF SENDING BUTTON MESSAGE
        send_button_message(sender_id, 'Button Template', [
            get_url_button('Google', 'https://www.google.com'),
            get_postback_button('Post it back!', 'PAYLOAD_POSTBACK')
            ])
    elif message_text == 'generic':
        # EXAMPLE OF SENDING GENERIC TEMPLATE
        fire_image_url = 'https://cdn.cloudpix.co/images/hot-wallpaper/fire-element-hd-wallpaper-hot-fire-wallpaper-4c0b34956dddc37694702630f23ab29a-large-1393949.jpg'
        water_image_url = 'http://vignette4.wikia.nocookie.net/elemental-roleplay/images/c/c6/Water_Element.jpeg/revision/latest?cb=20130912201151'
        send_generic_message(sender_id, [
                get_generic_element('Fire Element', 'Subtitle for fire element ~',
                fire_image_url,
                [get_url_button('go to pic', fire_image_url)]),
                get_generic_element('Water Element', 'Subtitle for water element ~',
                water_image_url,
                [get_url_button('go to pic', water_image_url),
                get_url_button('go to source page', 'http://elemental-roleplay.wikia.com/wiki/Water_Element')])
            ])
    elif message_text == 'receipt':
        # EXAMPLE OF SENDING RECEIPT TEMPLATE
        send_receipt_message(sender_id, [
            get_receipt_element('Dinner', 'Mala Hotpot', 4.20),
            get_receipt_element('Supper', 'Hawaiian Burger', 3.50)
        ], 7.70)
    elif message_text == 'quickreply':
        send_quick_reply(sender_id, 'What\'s your quick reply?', [
            get_quick_reply('A.', 'PAYLOAD_A'),
            get_quick_reply('B.', 'PAYLOAD_B'),
            get_quick_reply('C.', 'PAYLOAD_C'),
            get_quick_reply('NONE OF THE ABOVE.', 'PAYLOAD_NONE'),
        ])
    else:
        # NORMAL MESSAGE
        send_message(sender_id, 'Received ;)')

    if messaging_event['message'].get('quick_reply'):
        handle_quick_reply(messaging_event)

def handle_postback(messaging_event):
    print('received postback', messaging_event)
    sender_id = messaging_event['sender']['id'] # sender facebook ID
    payload = messaging_event.get('postback').get('payload')
    send_message(sender_id, 'Received postback ' + payload)

def handle_quick_reply(messaging_event):
    print('handle quick reply')
    sender_id = messaging_event['sender']['id'] # sender facebook ID
    payload = messaging_event['message']['quick_reply'].get('payload')
    send_message(sender_id, 'Received payload ' + payload)

def get_send_params():
    return {
        'access_token':
    }

def get_send_headers():
    return {
        'Content-Type': 'application/json'
    }

def get_url_button(title, url):
    return {
        'type': 'web_url',
        'url': url,
        'title': title
    }

def get_postback_button(title, payload):
    return {
        'type': 'postback',
        'title': title,
        'payload': payload
    }

def get_generic_element(title, subtitle, image_url, buttons):
    return {
        'title': title,
        'subtitle': subtitle,
        'image_url': image_url,
        'buttons': buttons
    }

def get_receipt_element(title, subtitle, price):
    return {
        'title': title,
        'subtitle': subtitle,
        'price': price
    }

def get_quick_reply(title, payload):
    return {
        'content_type': 'text',
        'title': title,
        'payload': payload
    }

def send_message(recipient_id, message_text):
    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text
        }
    })
    call_send_api(data)

def send_button_message(recipient_id, message_text, buttons):
    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': message_text,
                    'buttons': buttons
                }
            }
        }
    })
    call_send_api(data)

def send_generic_message(recipient_id, elements):
    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': elements
                }
            }
        }
    })
    call_send_api(data)

def send_receipt_message(recipient_id, elements, total_cost):
    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'receipt',
                    'recipient_name': 'N/A',
                    'order_number': 'N/A',
                    'currency': 'SGD',
                    'payment_method': 'N/A',
                    'summary': {
                        'total_cost': total_cost
                    },
                    'elements': elements
                }
            }
        }
    })
    call_send_api(data)

def send_typing_action(recipient_id):
    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'sender_action': 'typing_on'
    })
    call_send_api(data)

def send_quick_reply(recipient_id, message_text, quick_replies):
    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text,
            'quick_replies': quick_replies
        }
    })
    call_send_api(data)

def call_send_api(data):
    params = get_send_params()
    headers = get_send_headers()
    r = requests.post('https://graph.facebook.com/v2.6/me/messages', params=params, headers=headers, data=data)
    if r.status_code != 200:
        print('fail to send message')
        print(r.status_code)
        print(r.text)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
