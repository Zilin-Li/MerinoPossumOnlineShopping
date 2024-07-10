import re
from config import get_cursor
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..controllers.user_controllers import login_required, get_session_info
from ..controllers.product_controller import generate_card_number
from datetime import datetime

points = Blueprint(
    'points',
    __name__,
    static_folder='static',
    template_folder='templates'
)

@points.route('/')
@login_required
def view_customer_points():
    is_login, user_id, role_id,discount_rate = get_session_info()
    #get user points
    dbconn = get_cursor()
    dbconn.execute("SELECT point FROM customers WHERE user_id=%s", (user_id,))
    points = dbconn.fetchone()

    # get gift card types
    dbconn.execute("SELECT * FROM gift_cards_types where is_active=1")
    gift_card_types = dbconn.fetchall()

    #format gift card types data
    gift_card_types = [{'id': gift_card_type[0],'type_name':gift_card_type[1] , 'value': gift_card_type[2],'redeem_points':gift_card_type[4]} for gift_card_type in gift_card_types]
    return render_template('points/customer_points.html', points=points[0], gift_card_types=gift_card_types)


@points.route('/redeem', methods=['POST'])
@login_required
def redeem_gift_card():
    is_login, user_id, role_id,discount_rate = get_session_info()
    # get gift carad value from form
    gift_card_type_id = request.form.get('gift_card')  
    dbconn = get_cursor()
    dbconn.execute("SELECT point FROM customers WHERE user_id=%s", (user_id,))
    points = dbconn.fetchone()
    if not gift_card_type_id:
        flash('Please select a gift card amount.', 'error')
        return redirect(url_for('points.view_customer_points'))  
    # get the gift card value
    dbconn.execute("SELECT value FROM gift_cards_types WHERE id = %s", (gift_card_type_id,))
    card_value = dbconn.fetchone()
    card_value = int(card_value[0])

    if points[0] >= (card_value*10):     
        # new points balance
        new_points = points[0]-card_value*10
        create_gift_card(gift_card_type_id,card_value,dbconn)
        # update user points
        dbconn.execute("UPDATE customers SET point=%s WHERE user_id=%s", (new_points, user_id))
        # update point transaction
        dbconn.execute('INSERT INTO reward_transactions (point_change, transaction_date, user_id, order_id) VALUES (%s, NOW(), %s, %s)', (-(card_value*10), user_id, None))  
        flash('Gift card purchased successfully.', 'success')
        return redirect(url_for('points.view_customer_points'))
    else:
        flash('Insufficient points to redeem gift card', 'error')
        return redirect(url_for('points.view_customer_points'))



# function to generate a unique gift card code
def create_gift_card(value_type_id,card_value,dbconn):
    # get current user id
    is_login, user_id, role_id,discount_rate = get_session_info()

    # create a gift card code
    card_number = "BSMP"+generate_card_number(16)+"AK"
    message_content = "You have successfully purchased a gift card with the value of $"+str(card_value)+". Your gift card code is: "+card_number
    # store the gift card code in the database
    purchase_time = datetime.now()
    dbconn.execute("INSERT INTO gift_cards (user_id,type_id,card_number, balance, purchase_time) VALUES (%s, %s,%s,%s, %s)", (user_id,value_type_id, card_number, card_value,purchase_time))

    #send message to the user
    dbconn.execute("INSERT INTO messages (send_id, receive_id, message_content,created_at,message_type_id) VALUES (%s, %s,%s, %s, %s)", (4, user_id, message_content, datetime.now(),1))

   