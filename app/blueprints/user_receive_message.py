from flask import Blueprint, render_template, flash
from config import get_cursor
from ..controllers.user_controllers import get_session_info, login_required
from ..models.user_model import get_unread_messages,  get_message_info


# SCRUM-80 user receive message by Danfeng
user_receive_message = Blueprint(
    'user_receive_message',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# SCRUM-16 a Corporate Client is notified upon approval of account registration by Danfeng
# a user is notified after a new message arrived by Danfeng
@user_receive_message.route('/',methods=['GET'] )
@login_required  
def display_message():
    is_login, user_id, role_id, discount_rate = get_session_info()  
    unread_message_list = get_unread_messages(user_id) 
    return render_template('/user_message/user_receive_message.html',unread_message_list = unread_message_list) 
    
# the user view the detail of an unread message
@user_receive_message.route('/view_content/<int:message_id>', methods=['GET'])
@login_required    
def view_content(message_id):  
    message_detail = get_message_info(message_id) 
    try:    
        cursor = get_cursor() 
        cursor.execute("UPDATE messages SET is_read = %s WHERE id = %s", (1, message_id))
    except Exception as e:
        print(f"An error occurred: {e}")
        flash('An error occurred. Please try again later.', 'danger')  
    return render_template('/user_message/user_view_content.html',message_detail = message_detail)