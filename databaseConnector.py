import mysql.connector
import json
from datetime import datetime
from pprint import pprint
import uuid

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

    def get_category_id(self, category):
        cursor = DatabaseConnector.instance.cnx.cursor()
        query = "SELECT id FROM category WHERE name = %s"
        cursor.execute(query, (category, ))
        return cursor.fetchone()[0]

    def add_transaction(self, fb_user_id, item, amount, category='Others'):
        cursor = DatabaseConnector.instance.cnx.cursor()

        user_id = self.get_user_id(fb_user_id)
        if user_id is None:
            return

        category_id = self.get_category_id(category)

        query = "INSERT INTO transaction\
                    (item, amount, category_id, user_id)\
                    VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (item, amount, category_id, user_id))
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

    #end is a datetime
    def add_savings_goal(self, fb_user_id, item, amount, end):
        cursor = DatabaseConnector.instance.cnx.cursor()

        user_id = self.get_user_id(fb_user_id)
        if user_id is None:
            return

        if self.get_savings_goal(fb_user_id) is None:
            query = "INSERT INTO goal\
                        (item, amount, end, user_id)\
                        VALUES (%s, %s, %s, %s)"
        else:
            query = "UPDATE goal\
                        SET item = %s, amount = %s, end = %s\
                        WHERE user_id = %s"

        cursor.execute(query, (item, amount, end, user_id))
        DatabaseConnector.instance.cnx.commit()

    #end is a datetime
    def update_savings_goal_end(self, fb_user_id, end):
        cursor = DatabaseConnector.instance.cnx.cursor()

        savings_goal = self.get_savings_goal(fb_user_id)
        if savings_goal is None:
            return

        query = "UPDATE goal\
                    SET end = %s\
                    WHERE id = %s"

        cursor.execute(query, (end, savings_goal['id']))
        DatabaseConnector.instance.cnx.commit()

        savings_goal['end'] = end
        return savings_goal

    def get_savings_goal(self, fb_user_id):
        cursor = DatabaseConnector.instance.cnx.cursor()

        user_id = self.get_user_id(fb_user_id)
        if user_id is None:
            return None

        query = "SELECT id, item, amount, started, end\
                    FROM goal\
                    WHERE user_id = %s"
        cursor.execute(query, (user_id,))

        savings_goal = cursor.fetchone()

        if savings_goal is None:
            return None

        return {
            'id': savings_goal[0],
            'item': savings_goal[1],
            'amount': float(savings_goal[2]),
            'started': savings_goal[3],
            'end': savings_goal[4]
        }

    def get_session(self, fb_user_id):
        cursor = DatabaseConnector.instance.cnx.cursor()

        user_id = self.get_user_id(fb_user_id)
        if user_id is None:
            return None

        query = "SELECT uuid, context, modified\
                    FROM session\
                    WHERE user_id = %s"
        cursor.execute(query, (user_id, ))
        session = cursor.fetchone()

        current_time = datetime.utcnow()

        # session expired 20 minutes after last modified
        if session is None or (current_time - session[2]).total_seconds() > 20 * 60:
            new_uuid = uuid.uuid1()
            self.add_session(user_id, new_uuid) if session is None else self.update_session_id(new_uuid, user_id=user_id)
            return {
                'uuid': new_uuid,
                'context': '{}'
            }
        else:
            return {
                'uuid': session[0],
                'context': session[1]
            }

    def update_session_id(self, uuid, user_id='', fb_user_id=''):
        if user_id == '' and fb_user_id == '':
            return

        if user_id == '':
            user_id = self.get_user_id(fb_user_id)
            if user_id is None:
                return

        cursor = DatabaseConnector.instance.cnx.cursor()
        query = "UPDATE session\
                    SET uuid = %s, context = '{}'\
                    WHERE user_id = %s"
        cursor.execute(query, (str(uuid), user_id))
        DatabaseConnector.instance.cnx.commit()

    def update_session_context(self, uuid, context):
        cursor = DatabaseConnector.instance.cnx.cursor()
        query = "UPDATE session\
                    SET context = %s\
                    WHERE uuid = %s"
        cursor.execute(query, (context, str(uuid)))
        DatabaseConnector.instance.cnx.commit()

    def add_session(self, user_id, uuid, context='{}'):
        cursor = DatabaseConnector.instance.cnx.cursor()
        query = "INSERT INTO session\
                    (user_id, uuid, context)\
                    VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, str(uuid), context))
        DatabaseConnector.instance.cnx.commit()
