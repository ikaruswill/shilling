from databaseConnector import DatabaseConnector

class TransactionTask:
    def __init__(self, fb_user_id, item, amount):
        self.fb_user_id = fb_user_id
        self.item = item
        self.amount = amount

    def execute(self):
        DatabaseConnector().add_transaction(self.fb_user_id, self.item, self.amount)
