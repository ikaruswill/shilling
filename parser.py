from wit import Wit

class Parser:
    class __Parser:
        def __init__(self):
            self.witClient = Wit(access_token='%token%')

    instance = None
    def __init__(self):
        if not Parser.instance:
            Parser.instance = Parser.__Parser()
        else:
            Parser.instance

    def build_task(self, intent, reply='', item=None, amount=None):
        return {
            'reply': reply,
            'intent': intent,
            'item': item,
            'amount': amount
        }

    def wit_parse_message(self, message):
        if message == '':
            return self.build_task('reply', 'Where is the text? 🤔')
        resp = Parser.instance.witClient.message(message)
        entities = resp.get('entities')
        if entities:
            amount_of_money = entities.get('amount_of_money')
            item = entities.get('item')
            intent = entities.get('intent')
            if intent is not None:
                intent_value = intent[0]['value']
                if intent_value in ['summary', 'greet']:
                    return self.build_task(intent_value)
                elif amount_of_money is not None:
                    amount = amount_of_money[0]['value']
                    if intent_value == 'savings':
                        return self.build_task(
                                intent_value,
                                '',
                                'Income', amount
                            )
                    elif intent_value == 'goal' and item is not None:
                        item_value = item[0]['value']
                        amount = amount_of_money[0]['value']
                        return self.build_task(
                                intent_value,
                                'Want to buy ' + '$' + str(amount) + ' ' + item_value + '? For real? :O',
                                item_value, amount
                            )

            elif item is not None and amount_of_money is not None:
                item_value = item[0]['value']
                amount = amount_of_money[0]['value']
                return self.build_task(
                        'transaction', '', item_value, amount
                    )

        return self.build_task('reply', 'I don\'t think I understand ;). What would you like to do?')
