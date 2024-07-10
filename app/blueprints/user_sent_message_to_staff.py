from config import get_cursor
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..controllers.user_message_staff import insert_message
from ..controllers.user_controllers import login_required

user_sent_message_to_staff = Blueprint(
    'user_sent_message_to_staff',
    __name__,
    static_folder='static',
    template_folder='templates'
)


# User send message to staff with id 2
@user_sent_message_to_staff.route('/contact_us')
def contact_us():

    return render_template('footer_info/contact_us.html')

@user_sent_message_to_staff.route('/user_send_message_to_staff', methods=['GET', 'POST'])
@login_required
def user_send_message_to_staff():

    # check if current user is customer
    if session.get('role_id') == 1 or session.get('role_id') == 2:
        if request.method == 'POST':
            send_id = session.get('user_id')
            receive_id = 2
            message_content = request.form.get('message_content')

            # Insert message to database
            insert_message(send_id, receive_id, message_content, 2)
            flash('Message sent successfully!', 'success')
    else:
        flash("You don't have permission to send messages!", 'danger')
    return redirect(url_for('user_sent_message_to_staff.contact_us'))


# List all messages from staff
@user_sent_message_to_staff.route('/list_message_from_staff', methods=['GET', 'POST'])
def list_message_from_staff():
    # get user_id from session
    user_id = session.get('user_id')

    # connect to database
    dbconn = get_cursor()

    # get all messages from staff
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
        WHERE messages.receive_id = %s
        ORDER BY messages.is_read ASC, messages.created_at DESC
    '''

    dbconn.execute(query, (user_id,))
    messages = dbconn.fetchall()

    return render_template('messages/user_receive_staff_message.html', messages=messages)


# User get_message_content_details
@user_sent_message_to_staff.route('/user_message/<int:message_id>')
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

    return render_template('messages/user_message_staff_details.html', message=message)
