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

    def get_user_id(self, fb_user_id):
        cursor = DatabaseConnector.instance.cnx.cursor()
        query = "SELECT id FROM user WHERE app_user_id = %s"
        cursor.execute(query, (fb_user_id, ))
        return cursor.fetchone()[0]

    def add_transaction(self, fb_user_id, item, amount):
        cursor = DatabaseConnector.instance.cnx.cursor()

        user_id = self.get_user_id(fb_user_id)
        if user_id is None:
            return

        query = "INSERT INTO transaction\
                    (item, amount, category_id, user_id)\
                    VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (item, amount, 28, user_id))
        DatabaseConnector.instance.cnx.commit()

    def update_transaction(self, fb_user_id, category):
        cursor = DatabaseConnector.instance.cnx.cursor()

        user_id = self.get_user_id(fb_user_id)
        if user_id is None:
            return

        query = "UPDATE transaction\
                    SET category_id = (\
                        SELECT id FROM category\
                        WHERE name = %s\
                    )\
                    WHERE user_id = %s\
                    ORDER BY date DESC LIMIT 1"
        cursor.execute(query, (category, user_id))
        DatabaseConnector.instance.cnx.commit()

        return self.get_last_transaction(user_id)

    def get_last_transaction(self, user_id):
        cursor = DatabaseConnector.instance.cnx.cursor()

        query = "SELECT t.item, t.amount, c.name\
                    FROM transaction t, category c\
                    WHERE t.category_id = c.id\
                    AND t.user_id = %s\
                    ORDER BY date DESC LIMIT 1"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()

DatabaseConnector().get_summary
