from wit import Wit

access_token = ''

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
	entities = request['entities']

	# Status keys
	no_item_key = 'missingExpenseItem'
	no_amount_key = 'missingExpenseAmount'
	success_key = 'recordExpenseSuccess'

	# Entity keys
	item_key = 'expense_item'
	amount_key = 'amount_of_money'

	# Get keys if exists, else set to entity value
	item = context.setdefault(item_key, first_entity_value(entities, item_key))
	amount = context.setdefault(amount_key, first_entity_value(entities, amount_key))
		
	if item and amount:
		# Send data to DB
		context.pop(no_item_key)
		context.pop(no_amount_key)
		context[success_key] = True
	elif not amount:
		context.pop(no_item_key)
		context[no_amount_key] = True
		context.pop(success_key)
	elif not item:
		context[no_item_key] = True
		context.pop(no_amount_key)
		context.pop(success_key)
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

	# Status keys
	no_amount_key = 'missingIncomeAmount'
	success_key = 'recordIncomeSuccess'

	# Entity keys
	amount_key = 'amount_of_money'

	# Get keys if exists, else set to entity value
	amount = context.setdefault(amount_key, first_entity_value(entities, amount_key))

	if amount:
		# Send data to DB
		context.pop(no_amount_key)
		context[success_key] = True
	else:
		context[no_amount_key] = True
		context.pop(success_key)

	from pprint import pprint
	pprint(request)

	print('record_income(', amount, ')')
	
	return context

def show_summary(request):
	# Send user the summary link, using session_id key in request
	pass

def set_savings_goal(request):
	context = request['context']
	entities = request['entities']

	# Status keys
	no_item_key = 'missingGoalItem'
	no_amount_key = 'missingGoalAmount'
	success_key = 'setSavingsGoalSuccess'

	# Entity keys
	item_key = 'goal_item'
	amount_key = 'expense_item'

	# Get keys if exists, else set to entity value
	item = context.setdefault(item_key, first_entity_value(entities, item_key))
	amount = context.setdefault(amount_key, first_entity_value(entities, amount_key))
		
	if item and amount:
		# Send data to DB
		context.pop(no_item_key)
		context.pop(no_amount_key)
		context[success_key] = True
	elif not amount:
		context.pop(no_item_key)
		context[no_amount_key] = True
		context.pop(success_key)
	elif not item:
		context[no_item_key] = True
		context.pop(no_amount_key)
		context.pop(success_key)
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
client.interactive()