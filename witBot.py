from wit import Wit
import json
import uuid
from databaseConnector import DatabaseConnector

# access_token = '%token%'
access_token = 'FV6Z3EDSA7CHU7BGSXQRB23UVSYBQJSN'

def first_entity_value(entities, entity):
	if entity not in entities:
		return None
	val = entities[entity][0]['value']
	if not val:
		return None
	# val can be a dict or a primitive
	return val['value'] if isinstance(val, dict) else val

def send(request, response):
	print(response['text'])

def record_expense(request):
	context = request['context']
	print('record expense context', context)
	entities = request['entities']

	# State keys
	no_item_key = 'missingExpenseItem'
	no_amount_key = 'missingExpenseAmount'
	success_key = 'recordExpenseSuccess'

	# Entity keys
	item_key = 'expense_item'
	amount_key = 'amount_of_money'

	# Get keys from context if exists, else set to entity value
	item = context.get(item_key, None)
	amount = context.get(amount_key, None)
	if not item:
		item = first_entity_value(entities, item_key)
	if not amount:
		amount = first_entity_value(entities, amount_key)

	if item and amount:
		# Send data to DB
		context.pop(no_item_key, None)
		context.pop(no_amount_key, None)
		context[success_key] = True
		context['end'] = True
	elif not amount:
		context[item_key] = item
		context.pop(no_item_key, None)
		context[no_amount_key] = True
		context.pop(success_key, None)
	elif not item:
		context[amount_key] = amount
		context[no_item_key] = True
		context.pop(no_amount_key, None)
		context.pop(success_key, None)
	else:
		# Both is missing!?
		pass

	from pprint import pprint
	pprint(request)

	print('record_expense(', item, amount, ')')

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
		context['end'] = True
	else:
		context[no_amount_key] = True
		context.pop(success_key, None)

	from pprint import pprint
	pprint(request)

	print('record_income(', amount, ')')

	return context

def show_summary(request):
	# Send user the summary link, using session_id key in request
	request['end'] = True
	return request

def set_savings_goal(request):
	context = request['context']
	entities = request['entities']

	# Status keys
	no_item_key = 'missingGoalItem'
	no_amount_key = 'missingGoalAmount'
	success_key = 'setSavingsGoalSuccess'

	# Entity keys
	item_key = 'expense_item'
	amount_key = 'amount_of_money'

	# Get keys from context if exists, else set to entity value
	item = context.get(item_key, None)
	amount = context.get(amount_key, None)
	if not item:
		item = first_entity_value(entities, item_key)
	if not amount:
		amount = first_entity_value(entities, amount_key)

	if item and amount:
		# Send data to DB
		context.pop(no_item_key, None)
		context.pop(no_amount_key, None)
		context[success_key] = True
		context['end'] = True
	elif not amount:
		context[item_key] = item
		context.pop(no_item_key, None)
		context[no_amount_key] = True
		context.pop(success_key, None)
	elif not item:
		context[amount_key] = amount
		context[no_item_key] = True
		context.pop(no_amount_key, None)
		context.pop(success_key, None)
	else:
		# Both is missing!?
		pass


	from pprint import pprint
	pprint(request)

	print('set_savings_goal(', item, amount, ')')

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

fb_user_id = '1475963009142095'
while True:
	session = DatabaseConnector().get_session(fb_user_id)
	print('session', session)
	context = client.run_actions(session['uuid'], input("Say something: "), json.loads(session['context']))
	print('new context', context)
	if context.get('end') == True:
		DatabaseConnector().update_session_id(uuid.uuid1(), fb_user_id=fb_user_id)
	else:
		DatabaseConnector().update_session_context(session['uuid'], json.dumps(context))
