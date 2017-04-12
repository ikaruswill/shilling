from flask import Flask, jsonify, make_response, request, render_template
from flask_cors import CORS, cross_origin
from databaseConnector import DatabaseConnector
from datetime import datetime
from transactionTask import TransactionTask
from summaryTask import SummaryTask
from parser import Parser
from collections import OrderedDict
from dateutil.relativedelta import *
import os
import logging
import requests
import messengerHelper
import witBot

logging.basicConfig(filename='app.log',level=logging.DEBUG)

app = Flask(__name__, template_folder='./static')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

PAYLOAD_CATEGORIES = OrderedDict([('PAYLOAD_CAT_FOOD', 'Food'),
                                    ('PAYLOAD_CAT_TRANSPORT', 'Transport'),
                                    ('PAYLOAD_CAT_GROCERIES', 'Groceries'),
                                    ('PAYLOAD_CAT_ENTERTAINMENT', 'Entertainment'),
                                    ('PAYLOAD_CAT_BILLS', 'Bills'),
                                    ('PAYLOAD_CAT_RENTAL', 'Rental'),
                                    ('PAYLOAD_CAT_OTHERS', 'Others')])

PAYLOAD_MENUS = OrderedDict([('PAYLOAD_MENU_TRANSACTION', 'Record expenses'),
                            ('PAYLOAD_MENU_SAVINGS', 'Record income'),
                            ('PAYLOAD_MENU_GOALS', 'Set savings goal'),
                            ('PAYLOAD_MENU_SUMMARY', 'Show summary')])

PAYLOAD_GOAL_DURATION = OrderedDict([('PAYLOAD_GOAL_ONE_MONTH', 'One month'),
                                    ('PAYLOAD_GOAL_THREE_MONTHS', 'Three months'),
                                    ('PAYLOAD_GOAL_SIX_MONTHS', 'Six months'),
                                    ('PAYLOAD_GOAL_NINE_MONTHS', 'Nine months'),
                                    ('PAYLOAD_GOAL_ONE_YEAR', 'One Year')])

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
                messengerHelper.add_user_if_new(messaging_event)

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
@cross_origin()
def get_summary():
    user_id = request.args.get('userId')
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    if not user_id:
        return 'Missing userId parameter', 403
    elif not start_time:
        return 'Missing start parameter', 403
    elif not end_time:
        return 'Missing end parameter', 403

    try:
        int(start_time)
    except ValueError:
        return 'start parameter has to be integer', 403

    try:
        int(end_time)
    except ValueError:
        return 'end parameter has to be integer', 403

    return jsonify(DatabaseConnector().get_summary(user_id, start_time, end_time))

@app.route('/chart', methods=['GET'])
def get_chart_html():
    return render_template('index.html')

def handle_message(messaging_event):
    sender_id = messaging_event['sender']['id'] # sender facebook ID
    recipient_id = messaging_event['recipient']['id']  # our page ID
    message_text = messaging_event['message'].get('text') or ''

    logging.debug('received message ' + message_text)
    print('received message', message_text)

    messengerHelper.send_typing_action(sender_id)
    witBot.run_actions(sender_id, message_text)

def send_summary_template(sender_id):
    generated_url = SummaryTask(sender_id).execute()
    messengerHelper.send_generic_message(sender_id, [
        messengerHelper.get_generic_element('Expenses Summary', 'Chart view and table view', '', [
                messengerHelper.get_url_button('Show me', generated_url)
            ])
        ])

def send_menu_buttons(sender_id):
    menu_buttons = [messengerHelper.get_postback_button(PAYLOAD_MENUS[payload], payload) for payload in PAYLOAD_MENUS][0:3]
    messengerHelper.send_button_message(sender_id, 'Hi! What would you like to do?', menu_buttons)

def send_quick_reply_menu(sender_id, message):
    quick_replies = [messengerHelper.get_quick_reply(PAYLOAD_MENUS[p], p) for p in PAYLOAD_MENUS]
    messengerHelper.send_quick_reply(sender_id, message, quick_replies)

def handle_postback(messaging_event):
    print('received postback', messaging_event)
    sender_id = messaging_event['sender']['id'] # sender facebook ID
    handle_payload(sender_id, messaging_event.get('postback').get('payload'))

def handle_quick_reply(messaging_event):
    print('handle quick reply')
    sender_id = messaging_event['sender']['id'] # sender facebook ID
    handle_payload(sender_id, messaging_event['message']['quick_reply'].get('payload'))

def handle_payload(sender_id, payload):
    if payload.startswith('PAYLOAD_CAT'):
        handle_payload_cat(sender_id, payload)
    elif payload.startswith('PAYLOAD_MENU'):
        handle_payload_menu(sender_id, payload)
    elif payload.startswith('PAYLOAD_GOAL'):
        handle_payload_goal(sender_id, payload)
    else:
        messengerHelper.send_message(sender_id, 'Received payload ' + payload)

def handle_payload_cat(sender_id, payload):
    category = PAYLOAD_CATEGORIES[payload]
    transaction = DatabaseConnector().update_transaction(sender_id, category)
    messengerHelper.send_message(sender_id, get_expense_added_msg(transaction[0], -transaction[1], transaction[2]))

def handle_payload_menu(sender_id, payload):
    message = ''
    if payload == 'PAYLOAD_MENU_TRANSACTION':
        message = 'What did you spent on and how much is it?'
    elif payload == 'PAYLOAD_MENU_SAVINGS':
        message = 'Tell me how much is your income. For example: I got $20'
    elif payload == 'PAYLOAD_MENU_GOALS':
        message = 'What is your savings goal?'
    elif payload == 'PAYLOAD_MENU_SUMMARY':
        send_summary_template(sender_id)
        return

    messengerHelper.send_message(sender_id, message)

def handle_payload_goal(sender_id, payload):
    goal_start = DatabaseConnector().get_savings_goal(sender_id)['started']
    new_end = datetime.now()
    if payload == 'PAYLOAD_GOAL_ONE_MONTH':
        new_end = goal_start + relativedelta(months=+1)
    elif payload == 'PAYLOAD_GOAL_THREE_MONTHS':
        new_end = goal_start + relativedelta(months=+3)
    elif payload == 'PAYLOAD_GOAL_SIX_MONTHS':
        new_end = goal_start + relativedelta(months=+6)
    elif payload == 'PAYLOAD_GOAL_NINE_MONTHS':
        new_end = goal_start + relativedelta(months=+9)
    elif payload == 'PAYLOAD_GOAL_ONE_YEAR':
        new_end = goal_start + relativedelta(years=+1)

    savings_goal = DatabaseConnector().update_savings_goal_end(sender_id, new_end)
    messengerHelper.send_message(sender_id, get_goal_set_msg(savings_goal['item'], savings_goal['amount'], savings_goal['end'].date()))

def get_goal_set_msg(item, amount, end):
    return 'SAVINGS GOAL SET\nItem: {}\nPrice: ${}\nAchieve By: {}'.format(item, amount, end)

def get_expense_added_msg(item, price, category):
    return 'EXPENSE RECORDED\nItem: {}\nPrice: ${}\nCategory: {}'.format(item, price, category)

def get_income_added_msg(item, price):
    return 'INCOME RECORDED\nItem: {}\nPrice: ${}'.format(item, price)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
