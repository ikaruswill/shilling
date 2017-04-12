from wit import Wit
import json
import uuid
import messengerHelper
from databaseConnector import DatabaseConnector
from transactionTask import TransactionTask
from summaryTask import SummaryTask
from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import *

access_token = '%token%'
current_fb_user_id = ''

PAYLOAD_CATEGORIES = OrderedDict([('PAYLOAD_CAT_FOOD', 'Food'),
                                    ('PAYLOAD_CAT_TRANSPORT', 'Transport'),
                                    ('PAYLOAD_CAT_GROCERIES', 'Groceries'),
                                    ('PAYLOAD_CAT_ENTERTAINMENT', 'Entertainment'),
                                    ('PAYLOAD_CAT_BILLS', 'Bills'),
                                    ('PAYLOAD_CAT_RENTAL', 'Rental'),
                                    ('PAYLOAD_CAT_OTHERS', 'Others')])

PAYLOAD_GOAL_DURATION = OrderedDict([('PAYLOAD_GOAL_ONE_MONTH', 'One month'),
                                    ('PAYLOAD_GOAL_THREE_MONTHS', 'Three months'),
                                    ('PAYLOAD_GOAL_SIX_MONTHS', 'Six months'),
                                    ('PAYLOAD_GOAL_NINE_MONTHS', 'Nine months'),
                                    ('PAYLOAD_GOAL_ONE_YEAR', 'One Year')])

def first_entity_value(entities, entity):
	if entity not in entities:
		return None
	val = entities[entity][0]['value']
	if not val:
		return None
	# val can be a dict or a primitive
	return val['value'] if isinstance(val, dict) else val

def send(request, response):
	print('current_fb_user_id', current_fb_user_id)
	msg = response['text'].decode('utf-8')
	if response.get('quickreplies'):
		quick_replies = [messengerHelper.get_quick_reply(q, q) for q in response['quickreplies']]
		messengerHelper.send_quick_reply(current_fb_user_id, msg, quick_replies)
	else:
		messengerHelper.send_message(current_fb_user_id, msg)

def record_expense(request):
	context = request['context']
	entities = request['entities']

	# State keys
	no_item_key = 'missingExpenseItem'
	no_amount_key = 'missingExpenseAmount'
	no_category_key = 'missingExpenseCategory'
	success_key = 'recordExpenseSuccess'

	# Entity keys
	item_key = 'expense_item'
	amount_key = 'amount_of_money'
	category_key = 'category'

	# Get keys from context if exists, else set to entity value
	item = context.get(item_key, None)
	amount = context.get(amount_key, None)
	category = context.get(category_key, None)
	if not item:
		item = first_entity_value(entities, item_key)
	if not amount:
		amount = first_entity_value(entities, amount_key)
	if not category:
		category = first_entity_value(entities, category_key)


	if item and amount and category:
		# Send data to DB
		context[success_key] = True
		context['end'] = True

	if amount:
		context.pop(no_amount_key, None)
		context[amount_key] = amount
	else:
		context[no_amount_key] = True

	if item:
		context.pop(no_item_key, None)
		context[item_key] = item
	else:
		context[no_item_key] = True

	if category:
		context.pop(no_category_key, None)
		context[category_key] = category
	else:
		context[no_category_key] = True

	print('record_expense(', item, amount, ')', request)
	if context.get('end') == True:
		TransactionTask(current_fb_user_id, item, -amount, category).execute()

	return context

def record_income(request):
	context = request['context']
	entities = request['entities']

	# State keys
	no_amount_key = 'missingIncomeAmount'
	success_key = 'recordIncomeSuccess'

	# Entity keys
	amount_key = 'amount_of_money'

	amount = first_entity_value(entities, amount_key)

	if amount:
		# Send data to DB
		context.pop(no_amount_key, None)
		context[success_key] = True
		context[amount_key] = amount
		context['end'] = True
	else:
		context[no_amount_key] = True
		context.pop(success_key, None)

	print('record_income(', amount, ')')
	if context.get('end') == True:
		TransactionTask(current_fb_user_id, 'Income', amount).execute()
		messengerHelper.send_message(current_fb_user_id, get_income_added_msg(item, amount))

	return context

def show_summary(request):
	# Send user the summary link, using session_id key in request
	request['end'] = True
	generated_url = SummaryTask(current_fb_user_id).execute()
	messengerHelper.send_generic_message(current_fb_user_id, [
		messengerHelper.get_generic_element('Expenses Summary', 'Chart view and table view', '', [
				messengerHelper.get_url_button('Show me', generated_url)
			])
		])
	return request

def set_savings_goal(request):
	context = request['context']
	entities = request['entities']

	# Status keys
	no_item_key = 'missingGoalItem'
	no_amount_key = 'missingGoalAmount'
	no_duration_key = 'missingDuration'
	success_key = 'setSavingsGoalSuccess'

	# Entity keys
	item_key = 'expense_item'
	amount_key = 'amount_of_money'
	duration_key = 'duration'

	# Get keys from context if exists, else set to entity value
	item = context.get(item_key, None)
	amount = context.get(amount_key, None)
	duration = context.get(duration_key, None)
	if not item:
		item = first_entity_value(entities, item_key)
	if not amount:
		amount = first_entity_value(entities, amount_key)
	if not duration:
		duration = first_entity_value(entities, duration_key)

	if item and amount and duration:
		# Send data to DB
		context[success_key] = True
		context['end'] = True

	if amount:
		context.pop(no_amount_key, None)
		context[amount_key] = amount
	else:
		context[no_amount_key] = True

	if item:
		context.pop(no_item_key, None)
		context[item_key] = item
	else:
		context[no_item_key] = True

	if duration:
		context.pop(no_duration_key, None)
		context[duration_key] = item
	else:
		context[no_duration_key] = True

	print('set_savings_goal(', item, amount, duration, ')')

	if context.get('end') == True:
		months = 0
		if duration == '1 month':
			months = 1
		elif duration == '3 months':
			months = 3
		elif duration == '6 months':
			months = 6
		elif duration == '9 months':
			months = 9
		elif duration == '1 year':
			months = 12
		DatabaseConnector().add_savings_goal(current_fb_user_id, item, amount, datetime.now() + relativedelta(months=months))

	return context
	pass

actions = {
	'send': send,
	'recordExpense': record_expense,
	'recordIncome': record_income,
	'showSummary': show_summary,
	'setSavingsGoal': set_savings_goal
}
client = Wit(access_token=access_token, actions=actions)

def run_actions(fb_user_id, message):
	global current_fb_user_id
	current_fb_user_id = fb_user_id
	session = DatabaseConnector().get_session(fb_user_id)
	print('session', session)
	context = client.run_actions(session['uuid'], message, json.loads(session['context']))
	print('new context', context)
	if context.get('end') == True:
		DatabaseConnector().update_session_id(uuid.uuid1(), fb_user_id=fb_user_id)
	else:
		DatabaseConnector().update_session_context(session['uuid'], json.dumps(context))

def get_expense_added_msg(item, price, category):
    return 'EXPENSE RECORDED\nItem: {}\nPrice: ${}\nCategory: {}'.format(item, price, category)

def get_income_added_msg(item, price):
    return 'INCOME RECORDED\nItem: {}\nPrice: ${}'.format(item, price)
