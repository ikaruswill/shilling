from wit import Wit

access_token = ''

def first_entity_value(entities, entity):
	if entity not in entities:
		return None
	val = entities[entity][0]['value']
	if not val:
		return None
	return val['value'] if isinstance(val, dict) else val

def send(request, response):
	print(response['text'])

def record_expense(request):
	context = request['context']
	entities = request['entities']

	expense_item = first_entity_value(entities, 'expense_item')
	expense_amount = first_entity_value(entities, 'amount_of_money')

	if expense_item and expense_amount:
		# Send data to DB
		context.pop('missingExpenseItem', None)
		context.pop('missingExpenseAmount', None)
		context['recordExpenseSuccess'] = True
	elif expense_item:
		context.pop('recordExpenseSuccess', None)
		context.pop('missingExpenseItem', None)
		context['missingExpenseAmount'] = True
	elif expense_amount:
		context.pop('recordExpenseSuccess', None)
		context.pop('missingExpenseAmount', None)
		context['missingExpenseItem'] = True
	else:
		# Both is missing!?
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
		context.pop('missingAmount', None)
		context['recordIncomeSuccess'] = True
	else:
		context['missingAmount'] = True

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