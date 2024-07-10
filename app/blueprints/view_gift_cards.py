import re
from config import get_cursor
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..controllers.user_controllers import login_required, get_session_info, get_gift_card_info


view_gift_cards = Blueprint(
    'view_gift_cards',
    __name__,
    static_folder='static',
    template_folder='templates'
)

@view_gift_cards.route('/')
@login_required
def display_gift_cards():
    is_login, user_id, role_id,discount_rate = get_session_info()
    gift_cards =  get_gift_card_info(user_id)

    return render_template('customer_gift_cards/customer_gift_cards.html',gift_cards=gift_cards)


