import os
from collections import OrderedDict
from app.blueprints.users import users
from app.blueprints.staff import staff
from app.blueprints.manage_account import manage_account
from app.blueprints.categories import categories
from app.blueprints.cart import cart
from app.blueprints.user_message_staff import messages
from app.blueprints.record_status import staff_record_status
from app.blueprints.customer_track_order import customer_track_order
from app.blueprints.product_management import product_management

from app.blueprints.corporate_client_credit import corporate_client_credit
from app.blueprints.admin_manage_credit import admin_manage_credit
from app.blueprints.manager_manage_credit import manager_manage_credit
from app.blueprints.manager_popular_report import manager_popular_report
from app.blueprints.checkout import checkout
from app.blueprints.user_receive_message import user_receive_message
from app.blueprints.footer_info import footer_info
from app.blueprints.points import points
from app.blueprints.daily_orders_summary import daily_orders_summary
from app.blueprints.staff_manage_inventory import staff_manage_inventory
from app.blueprints.points import points
from app.blueprints.manager_monitor_client import manager_monitor_client
from app.blueprints.client_pay_invoice import client_pay_invoice

from app.blueprints.view_gift_cards import view_gift_cards
from app.blueprints.manage_gift_cards import manage_gift_cards

from app.blueprints.staff_product import staff_product
from app.blueprints.manage_promotion import manage_promotion
from app.blueprints.sales_trend_report import sales_trend_report
from app.blueprints.customer_demographics_report import customer_demographics_report
# New Message
from app.blueprints.user_sent_message_to_staff import user_sent_message_to_staff
from app.blueprints.staff_message_user import staff_message_user
from app.blueprints.manage_customer import manage_customer
from app.blueprints.manage_staff import manage_staff
from app.blueprints.send_news import send_news
from app.blueprints.manage_category import manage_category

import os
from dotenv import load_dotenv
from flask import Flask, render_template

from config import get_cursor
from flask import g, session, request
from app.controllers.user_controllers import get_session_info

# import blueprints
app = Flask(__name__)


@app.before_request
#  calculate the number of items in the cart
def load_cart_count():
    if request.path.startswith('/static/'):
        return  # Skip cart count loading for static files
    if 'customer_cart_items' not in g:
        # check if user is logged in
        if 'user_id' in session:
            cursor = get_cursor()
            cursor.execute("SELECT id FROM carts WHERE user_id=%s",
                           (session['user_id'],))
            cart = cursor.fetchone()
            # if user has a cart, get the total quantity of items in the cart
            if cart:
                cursor.execute(
                    "SELECT SUM(quantity) FROM cart_items WHERE cart_id=%s", (cart[0],))

                customer_cart_items = cursor.fetchone()[0]
                g.customer_cart_items = customer_cart_items if customer_cart_items else 0
            else:
                # if user does not have a cart, set the number of items in the cart to 0
                g.customer_cart_items = 0
        else:
            # if user is not logged in, set the number of items in the cart to 0
            g.customer_cart_items = 0


@app.before_request
# calculate the number of corporate client applications that need approval by the manager
def count_client_application():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if request.path.startswith('/static/'):
        return  # Skip pending application count for static files
    if 'count_client_application' not in g and session.get('is_manager') == 1:
        try:
            cursor = get_cursor()
            cursor.execute(
                "SELECT count(id) FROM corporate_clients WHERE is_approved=0")
            result = cursor.fetchone()
            g.count_client_application = result[0] if result else 0
        except Exception as e:
            print(f"An error occurred: {e}")
            g.count_client_application = 0
    else:
        # If user is not logged in, set the number of pending client applications to 0
        g.count_client_application = 0


@app.before_request
# calculate the number of messages that need to be read by the user
def count_message():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if request.path.startswith('/static/'):
        return  # Skip message count for static files

    if 'count_message' not in g and 'is_login' in session:
        try:
            cursor = get_cursor()
            cursor.execute(
                "SELECT count(id) FROM messages WHERE is_read=%s AND receive_id = %s", (0, user_id))
            result = cursor.fetchone()
            g.count_message = result[0] if result else 0

        except Exception as e:
            print(f"An error occurred: {e}")
            g.count_message = 0
    else:
        # If user is not logged in, set the number of message to 0
        g.count_message = 0


# calculate the number of messages that user received from staff
@app.before_request
def count_message_from_staff():
    session_info = get_session_info()
    user_id = session_info[1]  # get user_id from session
    # skip
    if request.path.startswith('/static/'):
        return
    if session_info[0] and 'count_message_from_staff' not in g:
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(id) FROM messages WHERE is_read=%s AND receive_id=%s", (0, user_id))
                result = cursor.fetchone()
                g.count_message_from_staff = result[0] if result else 0

        except Exception as e:
            print(f"An error occurred: {e}")
            g.count_message_from_staff = 0

# select the selected news
@app.before_request
def selected_news():
    if request.path.startswith('/static/'):
        return  # Skip message count for static files
    if 'selected_news' not in g:
        try:
            cursor = get_cursor()
            cursor.execute('SELECT news_content FROM news WHERE selected= 1')
            result = cursor.fetchone()
            g.selected_news = result[0] if result else []
        except Exception as e:
            print(f"An error occurred: {e}")
            g.selected_news = []
   

# cleanup the global variable after each request
@app.after_request
def cleanup(response):
    g.pop('count_client_application', None)
    g.pop('customer_cart_items', None)
    g.pop('count_message', None)
    g.pop('selected_news', None)
    return response

# This function is used to inject categories into the context of the application


@app.context_processor
def inject_categories():
    if 'categories' not in g:
        cursor = None
        try:
            cursor = get_cursor()

            cursor.execute(
                "SELECT * FROM categories WHERE parent_category_id IS NULL")
            categories = cursor.fetchall()
            categories = [dict(id=row[0], parent_category_id=row[1],
                               category_name=row[2], description=row[3]) for row in categories]
            for category in categories:
                cursor.execute(
                    "SELECT * FROM categories WHERE parent_category_id=%s", (category['id'],))
                subcategories = cursor.fetchall()
                category['subcategories'] = [
                    dict(id=row[0], parent_category_id=row[1],
                         subcategory_name=row[2], description=row[3])
                    for row in subcategories
                ]
            g.categories = categories
        finally:
            if cursor:
                cursor.close()
    return {'categories': g.categories}


# register blueprints for customers and corporate clients
app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(categories, url_prefix='/users/categories')
app.register_blueprint(cart, url_prefix='/users/cart')
app.register_blueprint(checkout, url_prefix='/users/checkout')
app.register_blueprint(manage_account, url_prefix='/users/manage_account')
app.register_blueprint(customer_track_order,
                       url_prefix='/users/customer_track_order')
app.register_blueprint(footer_info, url_prefix='/users/footer_info')
app.register_blueprint(points, url_prefix='/users/points')
app.register_blueprint(user_receive_message,
                       url_prefix='/users/user_receive_message')
app.register_blueprint(view_gift_cards, url_prefix='/users/view_gift_cards')

app.register_blueprint(user_sent_message_to_staff,
                       url_prefix='/users/user_sent_message_to_staff')


app.register_blueprint(staff, url_prefix='/staff')
app.register_blueprint(staff_record_status,
                       url_prefix='/staff/staff_record_status')
app.register_blueprint(daily_orders_summary,
                       url_prefix='/staff/daily_orders_summary')
app.register_blueprint(staff_manage_inventory,
                       url_prefix='/staff/staff_manage_inventory')
app.register_blueprint(staff_message_user,
                       url_prefix='/staff/staff_message_user')

app.register_blueprint(manager_manage_credit,
                       url_prefix='/manager/manager_manage_credit')

app.register_blueprint(manage_gift_cards,
                       url_prefix='/manager/manage_gift_cards')

app.register_blueprint(product_management, url_prefix='/manager/manage_products')

app.register_blueprint(messages, url_prefix='/messages')
app.register_blueprint(corporate_client_credit,
                       url_prefix='/corporate_client_credit')


app.register_blueprint(admin_manage_credit,
                       url_prefix='/admin/admin_manage_credit')


app.register_blueprint(manager_popular_report,
                       url_prefix='/manager/manager_popular_report')


# New Message

# app.register_blueprint(staff_message_user,
#                        url_prefix='/staff/staff_message_user')
app.register_blueprint(manager_monitor_client,
                       url_prefix='/manager/manager_monitor_client')
app.register_blueprint(sales_trend_report,
                       url_prefix='/sales_trend_report')
app.register_blueprint(customer_demographics_report,
                       url_prefix='/customer_demographics_report')
app.register_blueprint(client_pay_invoice,
                       url_prefix='/client/client_pay_invoice')

# staff Manage Product
app.register_blueprint(staff_product, url_prefix='/staff_product')

# Manager manage promotion
app.register_blueprint(manage_promotion, url_prefix='/manage_promotion')
app.register_blueprint(manage_customer, url_prefix='/manage_customer')
app.register_blueprint(manage_staff, url_prefix='/manage_staff')
app.register_blueprint(send_news, url_prefix='/send_news')
app.register_blueprint(manage_category, url_prefix='/admin/manage_category')

# load environment variables
load_dotenv()

# get environment variables for secret key
app.secret_key = os.environ.get('app_secret_key')


@app.route('/')
def home():
    
    return render_template('home/home.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)
