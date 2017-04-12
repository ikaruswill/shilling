from databaseConnector import DatabaseConnector

class SummaryTask:
    def __init__(self, fb_user_id):
        self.fb_user_id = fb_user_id

    def execute(self):
        # generate link
        user_id = DatabaseConnector().get_user_id(self.fb_user_id)
        return 'https://shilling.ikaruswill.com/chart?userId={}'.format(user_id)
