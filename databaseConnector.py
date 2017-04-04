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
                    WHERE t.date BETWEEN %s AND %s\
                    AND t.user_id = user_id\
                    AND t.category_id = c.id"
        cursor.execute(query,
            (datetime.utcfromtimestamp(int(start_time) / 1000.0),
            datetime.utcfromtimestamp(int(end_time) / 1000.0)))

        epoch = datetime.utcfromtimestamp(0)
        return [{
            'item': item,
            'amount': float(amount),
            'category_id': category_id,
            'date': (date - epoch).total_seconds() * 1000
        } for (item, amount, category_id, date) in cursor]
