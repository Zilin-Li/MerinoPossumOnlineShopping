from config import get_cursor


# Insert a message to the database
def insert_message(send_id, receive_id, message_content, message_type_id):
    dbconn = get_cursor()
    dbconn.execute(
        "INSERT INTO messages (send_id, receive_id, message_content, message_type_id) VALUES (%s, %s, %s, %s)",
        (send_id, receive_id, message_content, message_type_id)
    )
