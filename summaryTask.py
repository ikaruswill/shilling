from databaseConnector import DatabaseConnector
from datetime import datetime

class SummaryTask:
    def __init__(self, fb_user_id):
        self.fb_user_id = fb_user_id

    def execute(self):
        # generate link
        user_id = DatabaseConnector().get_user_id(self.fb_user_id)
        epoch = datetime.utcfromtimestamp(0)
        end_time = int((datetime.now() - epoch).total_seconds() * 1000)
        start_time = end_time - 24 * 60 * 60 * 1000
        return 'https://shilling.ikaruswill.com/chart?userId={}&start={}&end={}'.format(user_id, start_time, end_time)
