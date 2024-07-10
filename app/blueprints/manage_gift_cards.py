import re
from config import get_cursor
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..controllers.user_controllers import login_required, get_session_info

manage_gift_cards = Blueprint(
    'manage_gift_cards',
    __name__,
    static_folder='static',
    template_folder='templates'
)

@manage_gift_cards.route('/')
@login_required
def display_gift_card_types():
    is_login, user_id, role_id,discount_rate = get_session_info()
    is_manager =session.get('is_manager', False)
    is_admin = session.get('is_admin', False)
    if is_admin or is_manager:
    # get gift card types
        cursor = get_cursor()
        cursor.execute("SELECT * FROM gift_cards_types ORDER BY is_active DESC, id ASC;")
        gift_card_types = cursor.fetchall()
        return render_template('manage_reward_giftcard/manage_reward_giftcard.html', gift_card_types= gift_card_types)
    else:
        flash('You are not authorized to access this page.🚫', 'danger')
        return redirect(url_for('users.login'))

@manage_gift_cards.route('/update_redeem_points', methods=['POST'])
@login_required
def update_redeem_points():
    is_login, user_id, role_id,discount_rate = get_session_info()
    is_manager =session.get('is_manager', False)
    is_admin = session.get('is_admin', False)
    if is_admin or is_manager:
        redeem_points = request.form.get('redeem_points')
        type_id = request.form.get('type_id')
        print(redeem_points, type_id)
        cursor = get_cursor()
        cursor.execute("UPDATE gift_cards_types SET redeem_points=%s WHERE id=%s", (redeem_points,type_id,))
        flash('Redeem points updated successfully.✅', 'success')
        return redirect(url_for('manage_gift_cards.display_gift_card_types'))
    else:
        flash('You are not authorized to access this page.🚫', 'danger')
        return redirect(url_for('users.login'))

@manage_gift_cards.route('/update_card_type/<int:type_id>', methods=['GET'])
@login_required
def update_card_type(type_id):
    is_login, user_id, role_id,discount_rate = get_session_info()
    is_manager =session.get('is_manager', False)
    is_admin = session.get('is_admin', False)
    if is_admin or is_manager:
        cursor = get_cursor()
        cursor.execute("SELECT * FROM gift_cards_types WHERE id=%s", (type_id,))
        card_type_detail = cursor.fetchone()
        # format the card type detail
        card_type_detail = {
            'id': card_type_detail[0],
            'type_name': card_type_detail[1],
            'value': card_type_detail[2],
            'redeem_points': card_type_detail[4],
            'description': card_type_detail[3],
            'is_active': card_type_detail[5]
        }
        return render_template('manage_reward_giftcard/update_card_type.html', card_type_detail=card_type_detail)
    else:
        flash('You are not authorized to access this page.🚫', 'danger')
        return redirect(url_for('users.login'))

@manage_gift_cards.route('/update_card_type_submit', methods=['POST'])
@login_required
def update_card_type_submit():
    is_login, user_id, role_id,discount_rate = get_session_info()
    is_manager =session.get('is_manager', False)
    is_admin = session.get('is_admin', False)
    if is_admin or is_manager:
        type_id = request.form.get('type_id')
        value = request.form.get('card_value')
        description = request.form.get('card_description')
        status = request.form.get('status')

        cursor = get_cursor()
        cursor.execute("UPDATE gift_cards_types SET  value=%s, description=%s,is_active=%s WHERE id=%s", (value,  description, status,type_id,))
        flash('Card type updated successfully.✅', 'success')
        return redirect(url_for('manage_gift_cards.update_card_type', type_id=type_id))
    else:
        flash('You are not authorized to access this page.🚫', 'danger')
        return redirect(url_for('users.login'))

@manage_gift_cards.route('/add_new_card_type')
@login_required
def add_new_card_type():
    is_login, user_id, role_id,discount_rate = get_session_info()  
    is_admin = session.get('is_admin', False)
    if is_admin:
        return render_template('manage_reward_giftcard/add_new_card_type.html')
    else:
        flash('You are not authorized to access this page.🚫', 'danger')
        return redirect(url_for('users.login'))

@manage_gift_cards.route('/add_new_card_type_submit', methods=['POST'])
@login_required
def add_card_type_submit():
    is_login, user_id, role_id,discount_rate = get_session_info()
    is_admin = session.get('is_admin', False)
    if is_admin:
        type_name = request.form.get('card_type_name')
        value = request.form.get('card_value')
        redeem_points = request.form.get('redeem_points')
        description = request.form.get('card_description')
        status = request.form.get('status')
        
        cursor = get_cursor()
        cursor.execute("INSERT INTO gift_cards_types (type_name, value, description, redeem_points,is_active) VALUES (%s, %s,%s, %s, %s)", (type_name, value, description, redeem_points,status,))
        flash('New card type added successfully.✅', 'success')
        return redirect(url_for('manage_gift_cards.display_gift_card_types'))
    else:
        flash('You are not authorized to access this page.🚫', 'danger')
        return redirect(url_for('users.login'))