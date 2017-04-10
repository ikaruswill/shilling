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

	no_item_key = 'missingExpenseItem'
	no_amount_key = 'missingExpenseAmount'
	success_key = 'recordExpenseSuccess'

	item_key = 'expense_item'
	amount_key = 'amount_of_money'

	# Get keys if exists, else set to entity value
	expense_item = context.setdefault(item_key, first_entity_value(entities, item_key))
	expense_amount = context.setdefault(amount_key, first_entity_value(entities, amount_key))
		
	if expense_item and expense_amount:
		# Send data to DB
		context.pop(no_item_key)
		context.pop(no_amount_key)
		context.set(success_key, True)
	elif not expense_amount:
		context.pop(no_item_key)
		context.set(no_amount_key, True)
		context.pop(success_key)
	elif not expense_item:
		context.set(no_item_key, True)
		context.pop(no_amount_key)
		context.pop(success_key)
	else:
		"# Both is missing!?"
		pass

	from pprint import pprint
	pprint(request)

	print('record_expense(', expense_item, expense_amount, ')')
	
	return context

def record_income(request):
	context = request['context']
	entities = request['entities']

	income_amount = first_entity_value(entities, 'amount_of_money')
	if income_amount:
		# Send data to DB
		context.pop('missingIncomeAmount', None)
		context['recordIncomeSuccess'] = True
	else:
		context['missingIncomeAmount'] = True

	from pprint import pprint
	pprint(request)

	print('record_income(', income_amount, ')')
	
	return context

def show_summary(request):
	# Send user the summary link, using session_id key in request
	pass

def set_savings_goal(request):
	context = request['context']
	entities = request['entities']

	goal_item = first_entity_value(entities, 'expense_item')
	goal_amount = first_entity_value(entities, 'amount_of_money')

	if goal_item and goal_amount:
		# Send data to DB
		context.pop('missingGoalItem', None)
		context.pop('missingGoalAmount', None)
		context['setSavingsGoalSuccess'] = True
	elif goal_item:
		context.pop('setSavingsGoalSuccess', None)
		context.pop('missingGoalItem', None)
		context['missingGoalAmount'] = True
	elif goal_amount:
		context.pop('setSavingsGoalSuccess', None)
		context.pop('missingGoalAmount', None)
		context['missingGoalItem'] = True
	else:
		# Both is missing!?
		pass

	from pprint import pprint
	pprint(request)
	
	print('set_savings_goal(', goal_item, goal_amount, ')')

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