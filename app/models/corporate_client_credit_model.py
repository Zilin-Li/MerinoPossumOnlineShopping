import mysql.connector as mysql_connector
from config import dbuser, dbpassword, dbhost, dbport, dbname

def get_credit_info_from_db(user_id):
    connection = mysql_connector.connect(
        user=dbuser,
        password=dbpassword,
        host=dbhost,
        port=dbport,
        auth_plugin='mysql_native_password',
        database=dbname,
        autocommit=True
    )
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT cc.credit_limit, cc.available_credit
            FROM corporate_clients cc
            JOIN users u ON cc.user_id = u.id
            WHERE cc.user_id = %s
        """, (user_id,))
        credit_info = cursor.fetchone()
    except Exception as e:
        print(f"Error: {e}")
        credit_info = None
    finally:
        cursor.close()
        connection.close()
    return credit_info

# Function to insert a credit limit increase request into the database
def insert_credit_limit_increase_request(user_id, requested_limit):
    connection = mysql_connector.connect(
        user=dbuser,
        password=dbpassword,
        host=dbhost,
        port=dbport,
        auth_plugin='mysql_native_password',
        database=dbname,
        autocommit=True
    )
    cursor = connection.cursor()
    try:
        # Insert a new credit limit increase request
        cursor.execute("""
            INSERT INTO credit_limit_increase_requests (user_id, requested_limit, status)
            VALUES (%s, %s, 'Pending')
        """, (user_id, requested_limit))
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()





