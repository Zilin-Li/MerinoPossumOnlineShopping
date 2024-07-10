from config import get_cursor
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..controllers.user_message_staff import insert_message

staff_message_user = Blueprint(
    'staff_message_user',
    __name__,
    static_folder='static',
    template_folder='templates'
)


# list all of message that received from user
@staff_message_user.route('/staff_message_user')
def list_message_received_from_user():
    # Connect to the database
    dbconn = get_cursor()

    # Query all messages with message type name
    query = '''
        SELECT
            messages.id AS message_id,
            messages.message_content,
            messages.created_at,
            messages.is_read,
            send_user.username AS sender_username,
            receive_user.username AS receiver_username,
            message_type.message_type_name AS message_type_name
        FROM messages
        JOIN users AS send_user ON messages.send_id = send_user.id
        JOIN users AS receive_user ON messages.receive_id = receive_user.id
        JOIN message_type ON messages.message_type_id = message_type.id
        WHERE messages.receive_id = 2
        ORDER BY messages.is_read ASC, messages.created_at DESC
    '''
    dbconn.execute(query)
    messages = dbconn.fetchall()

    return render_template('messages/staff_message_user.html', messages=messages)


# Get message content details
@staff_message_user.route('/staff_message_user/<int:message_id>')
def get_message_content_details(message_id):
    # Connect to the database
    dbconn = get_cursor()

    # Query message content details
    dbconn.execute("SELECT * FROM messages WHERE id = %s", (message_id,))
    message = dbconn.fetchone()

    if message:
        # Update is_read to True
        dbconn.execute(
            "UPDATE messages SET is_read = TRUE WHERE id = %s", (message_id,))

    return render_template('messages/staff_message_user_details.html', message=message)


# staff replay message to user
@staff_message_user.route('/staff_message_user/<int:receive_id>/reply', methods=['GET', 'POST'])
def reply_message(receive_id):
    # check if user role
    if session.get('role_id') == 3 or session.get('user_id') == 2:
        if request.method == 'POST':
            send_id = session.get('user_id')
            message_content = request.form.get('message_content')
            # Insert message to database
            insert_message(send_id, receive_id, message_content, 2)
            # update is_read to True
            dbconn = get_cursor()
            dbconn.execute(
                "UPDATE messages SET is_read = TRUE WHERE id = %s", (receive_id,))
            flash('Your message has been sent successfully.', 'success')
            return redirect(url_for('staff_message_user.list_message_received_from_user'))
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('home'))

    return render_template('messages/staff_message_user_reply.html')
