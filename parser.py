from wit import Wit

class Parser:
    class __Parser:
        def __init__(self):
            self.witClient = Wit(access_token='')

    instance = None
    def __init__(self):
        if not Parser.instance:
            Parser.instance = Parser.__Parser()
        else:
            Parser.instance

    def wit_parse_message(self, message):
        if message == '':
            return 'Where is the text? 🤔'
        resp = Parser.instance.witClient.message(message)
        entities = resp.get('entities')
        if entities:
            amount_of_money = entities.get('amount_of_money')
            item = entities.get('item')
            intent = entities.get('intent')
            if intent is not None:
                if intent[0]['value'] == 'summary':
                    return 'Ok ok show you summary later'
                elif amount_of_money is not None:
                    if intent[0]['value'] == 'savings':
                        return 'Wah nowadays got people save money one a? ' + amount_of_money[0]['value'] + ' only, might as well don\'t save'
                    elif intent[0]['value'] == 'goal' and item is not None:
                        return 'Want to buy ' + '$' + str(amount_of_money[0]['value']) + ' ' + item[0]['value'] + '? For real? :O'
            elif item is not None and amount_of_money is not None:
                return 'Add transaction:\nItem: ' + item[0]['value'] + '\nPrice: ' + '$' + str(amount_of_money[0]['value'])

        return 'I don\'t think I understand ;)'
