import mysql.connector as mysql_connector
from config import get_cursor, dbuser, dbpassword, dbhost, dbport, dbname

def get_cursor_and_connection():
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
    return connection, cursor

def get_credit_info_from_db(user_id):
    cursor = get_cursor()
    cursor.execute("SELECT company_name, credit_limit, available_credit, discount_level, is_approved FROM corporate_clients WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return {
            'company_name': result[0],
            'credit_limit': result[1],
            'available_credit': result[2],
            'discount_level': result[3],
            'is_approved': result[4]
        }
    return None

def insert_credit_limit_increase_request(user_id, requested_limit):
    connection, cursor = get_cursor_and_connection()
    cursor.execute(
        "INSERT INTO credit_limit_increase_requests (user_id, requested_limit, status) VALUES (%s, %s, %s)",
        (user_id, requested_limit, 'Pending')
    )
    connection.commit()
    cursor.close()
    connection.close()

def update_credit_limit(user_id, new_limit):
    connection, cursor = get_cursor_and_connection()
    cursor.execute("UPDATE corporate_clients SET credit_limit = %s WHERE user_id = %s", (new_limit, user_id))
    connection.commit()
    cursor.close()
    connection.close()

def fetch_all_clients():
    cursor = get_cursor()
    cursor.execute("""
        SELECT cc.user_id, cc.company_name, cc.credit_limit, cc.available_credit, 
               (SELECT COUNT(*) FROM credit_limit_increase_requests clr 
                WHERE clr.user_id = cc.user_id AND clr.status = 'Pending') AS has_pending_request
        FROM corporate_clients cc
    """)
    clients = cursor.fetchall()
    cursor.close()
    return clients

def fetch_credit_limit_increase_requests(user_id):
    cursor = get_cursor()
    cursor.execute("""
        SELECT id, requested_limit, request_date, status 
        FROM credit_limit_increase_requests 
        WHERE user_id = %s AND status = 'Pending'
    """, (user_id,))
    requests = cursor.fetchall()
    cursor.close()
    return requests

def approve_credit_limit_request(request_id):
    connection, cursor = get_cursor_and_connection()
    cursor.execute("SELECT user_id, requested_limit FROM credit_limit_increase_requests WHERE id = %s", (request_id,))
    request = cursor.fetchone()
    user_id, requested_limit = request[0], request[1]
    cursor.execute("UPDATE corporate_clients SET credit_limit = %s WHERE user_id = %s", (requested_limit, user_id))
    cursor.execute("UPDATE credit_limit_increase_requests SET status = 'Approved', approved = TRUE, approved_date = NOW() WHERE id = %s", (request_id,))
    connection.commit()
    cursor.close()
    connection.close()












