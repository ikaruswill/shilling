from databaseConnector import DatabaseConnector
import requests
import json

def get_send_params():
    return {
        'access_token': '%token%'
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

def after_request(r):
    if r.status_code != 200:
        print('fail to send message')
        print(r.status_code)
        print(r.text)

def call_send_api(data):
    params = get_send_params()
    headers = get_send_headers()
    r = requests.post('https://graph.facebook.com/v2.6/me/messages', params=params, headers=headers, data=data)
    after_request(r)

def get_user_profile(fb_user_id):
    params = get_send_params()
    headers = get_send_headers()
    r = requests.get('https://graph.facebook.com/v2.6/' + fb_user_id + '?fields=first_name,last_name', params=params, headers=headers)
    after_request(r)
    return json.loads(r.text)

def add_user_if_new(messaging_event):
    sender_id = messaging_event['sender']['id'] # sender facebook ID
    user_profile = get_user_profile(sender_id)
    if user_profile.get('first_name') and user_profile.get('last_name'):
        DatabaseConnector().add_user(user_profile['first_name'], user_profile['last_name'], sender_id)
