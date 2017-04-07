import mysql.connector
import json
from datetime import datetime
from pprint import pprint

class DatabaseConnector:
    class __DatabaseConnector:
        def __init__(self):
            self.cnx = mysql.connector.connect(user='shilling', password='ccsksnicwill',
                                          host='shilling.ikaruswill.com',
                                          database='shilling')
    instance = None
    def __init__(self):
        if not DatabaseConnector.instance:
            DatabaseConnector.instance = DatabaseConnector.__DatabaseConnector()
        else:
            DatabaseConnector.instance

    def get_summary(self, user_id, start_time, end_time):
        cursor = DatabaseConnector.instance.cnx.cursor()
        query = "SELECT t.item, t.amount, c.name, t.date\
                    FROM transaction t, category c\
                    WHERE (t.date BETWEEN %s AND %s)\
                    AND t.user_id = %s\
                    AND t.category_id = c.id"
        cursor.execute(query,
            (datetime.utcfromtimestamp(int(start_time) / 1000.0),
            datetime.utcfromtimestamp(int(end_time) / 1000.0),
            user_id))

        epoch = datetime.utcfromtimestamp(0)
        return [{
            'item': item,
            'amount': float(amount),
            'category_id': category_id,
            'date': (date - epoch).total_seconds() * 1000
        } for (item, amount, category_id, date) in cursor]

    def add_user(self, first_name, last_name, fb_user_id):
        cursor = DatabaseConnector.instance.cnx.cursor()

        query = "SELECT count(*) FROM user WHERE app_user_id = %s"
        cursor.execute(query, (fb_user_id, ))
        count = cursor.fetchone()[0]
        if count is not None and count > 0:
            return

        query = "INSERT INTO user\
                    (first_name, last_name, app_user_id)\
                    VALUES (%s, %s, %s)"
        cursor.execute(query, (first_name, last_name, fb_user_id))
        DatabaseConnector.instance.cnx.commit()

    def add_transaction(self, fb_user_id, item, amount):
        cursor = DatabaseConnector.instance.cnx.cursor()

        query = "SELECT id FROM user WHERE app_user_id = %s"
        cursor.execute(query, (fb_user_id, ))
        user_id = cursor.fetchone()[0]
        if user_id is None:
            return

        query = "INSERT INTO transaction\
                    (item, amount, category_id, user_id)\
                    VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (item, amount, 1, user_id))
        DatabaseConnector.instance.cnx.commit()

DatabaseConnector().get_summary
