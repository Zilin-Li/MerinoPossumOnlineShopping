from config import get_cursor
from flask import Blueprint, flash, render_template, request, redirect, url_for, session


messages = Blueprint(
    'messages',
    __name__,
    static_folder='static',
    template_folder='templates'
)


@messages.route('user_message/', methods=['GET', 'POST'])
def user_message():
    # check if current user is customer
    if session.get('role_id') == 1:
        dbconn = get_cursor()
        # get all staff users
        dbconn.execute("SELECT * FROM users WHERE role_id = '3'")
        staff_users = dbconn.fetchall()
        # current users send message to one of the staff
        if request.method == 'POST':
            sender_id = session.get('user_id')
            receiver_id = request.form.get('receiver_id')
            message_content = request.form.get('message_content')
            # Insert the message into the messages table
            dbconn.execute("INSERT INTO messages (send_id, receive_id, message_content, message_type_id) VALUES (%s, %s, %s, %s)",
                           (sender_id, receiver_id, message_content, 3)
                           )
        # list all message received by the current user
        dbconn.execute("SELECT * FROM messages WHERE receive_id = %s",
                       (session.get('user_id'),))
        messages = dbconn.fetchall()

        flash('Message sent successfully!', 'success')

    else:
        flash('You are not a customer!', 'danger')
        return redirect(url_for('home'))

    return render_template('messages/user_messages.html', staff_users=staff_users, messages=messages)


@messages.route('staff_message/', methods=['GET', 'POST'])
def staff_message():
    # check if current user is staff
    if session.get('role_id') == 3:
        dbconn = get_cursor()
        # Get all messages with sender's username and is_read = False

        dbconn.execute("SELECT messages.*, sender.username AS sender_username FROM messages JOIN users AS sender ON messages.send_id = sender.id WHERE messages.receive_id = %s AND messages.is_read = FALSE",
                       (session.get('user_id'),))
        messages = dbconn.fetchall()

        flash('Message sent successfully!', 'success')
    else:
        flash('You are not a staff!', 'danger')
        return redirect(url_for('home'))

    return render_template('messages/staff_message.html', messages=messages)


@messages.route('staff_reply_user/<int:receive_id>', methods=['GET', 'POST'])
def staff_reply_user(receive_id):
    # check if current user is staff
    if session.get('role_id') == 3:
        dbconn = get_cursor()
        if request.method == 'POST':
            sender_id = session.get('user_id')
            message_content = request.form.get('message_content')
            # Insert the message into the messages table
            dbconn.execute("INSERT INTO messages (send_id, receive_id, message_content, message_type_id) VALUES (%s, %s, %s, %s)",
                           (sender_id, receive_id, message_content, 3)
                           )

            flash('Message sent successfully!', 'success')
            return redirect(url_for('messages.staff_message'))

    else:
        flash('You are not a staff!', 'danger')
        return redirect(url_for('home'))

    return render_template('messages/staff_reply_user.html', receive_id=receive_id)


# @messages.route('staff_read_message/<int:receive_id>', methods=['GET', 'POST'])
# def staff_read_message(receive_id):
#     # check if current user is staff
#     if session.get('role_id') == 3:
#         dbconn = get_cursor()
#         # update is_read to True for the selected message
#         dbconn.execute("UPDATE messages SET is_read = TRUE WHERE receive_id = %s",
#                        (receive_id,))

#         flash('Message read successfully!', 'success')

#     else:
#         flash('You are not a staff!', 'danger')
#         return redirect(url_for('home'))

#     return redirect(url_for('messages.staff_message'))


# @messages.route('staff_delate_message/<int:receive_id>', methods=['GET', 'POST'])
# def staff_delate_message(receive_id):
#     # check if current user is staff
#     if session.get('role_id') == 3:
#         dbconn = get_cursor()
#         # delete the selected message
#         dbconn.execute("DELETE FROM messages WHERE receive_id = %s",
#                        (receive_id,))
#         flash('Message deleted successfully!', 'success')

#         return redirect(url_for('messages.staff_message'))
#     else:
#         flash('You are not a staff!', 'danger')
#         return redirect(url_for('home'))


@messages.route('/notification', methods=['GET', 'POST'])
def natification():
    # check if current has an order
    if session.get('role_id') == 1:
        dbconn = get_cursor()
        # check if the user has an order
        dbconn.execute("SELECT * FROM orders WHERE user_id = %s AND status_id = 1",
                       (session.get('user_id'),)
                       )
        order = dbconn.fetchone()
        if order:
            # check order status
            if order[6] == 1:
                # push notification to user
                flash('Waiting for processing', 'info')
            elif order[6] == 2:
                # push notification to user
                flash('Currently being processed', 'info')

            elif order[6] == 3:
                # push notification to user
                flash('Order has been shipped out', 'info')
            else:
                # push notification to user
                flash('Order has been delivered', 'info')

    return render_template('messages/natification.html', order=order)
