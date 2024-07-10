from config import get_cursor
from flask import flash

# get all users
def get_users():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return users

# get all unread messages for a user by Danfeng
def get_unread_messages(user_id):
    cursor = get_cursor()
    unread_message_list = []
    try:
        sql="""
            SELECT m.id, mt.message_type_name, m.created_at, e.job_title, u.first_name, u.last_name
            FROM messages m
            JOIN message_type mt ON m.message_type_id = mt.id  
            JOIN users u ON m.send_id = u.id JOIN employees e ON u.id = e.user_id
            WHERE is_read = %s AND receive_id=%s
        """
        cursor.execute(sql, (0, user_id))
        unread_message_list = cursor.fetchall()  
        return  unread_message_list                 
    except Exception as e:
        print(f"An error occurred: {e}")  
        flash('An error occurred. Please try again later.', 'danger') 
        return unread_message_list             

# a user gets the details of a message after it arriveds by Danfeng
def get_message_info(message_id):
    cursor = get_cursor()
    message_detail = []
    try:
        sql="""
            SELECT mt.message_type_name, m.message_content
            FROM messages m
            JOIN message_type mt ON m.message_type_id = mt.id  
            WHERE m.id = %s
        """
        cursor.execute(sql, (message_id,))
        message_detail = cursor.fetchone()  
        return  message_detail                 
    except Exception as e:
        print(f"An error occurred: {e}")  
        flash('An error occurred. Please try again later.', 'danger') 
        return message_detail             
    


def get_gift_card_info(user_id):
    cursor = get_cursor()
    gift_card_list = []
    try:
        sql="""
            SELECT 
                g.id,
                g.card_number,
                g.balance,
                g.purchase_time,
                t.type_name,
                t.value
            FROM gift_cards g
            JOIN gift_cards_types t ON g.type_id = t.id
            WHERE g.user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        gift_card_list = cursor.fetchall()  
        return  gift_card_list                 
    except Exception as e:
        print(f"An error occurred: {e}")  
        flash('An error occurred. Please try again later.', 'danger') 
        return gift_card_list             
   
