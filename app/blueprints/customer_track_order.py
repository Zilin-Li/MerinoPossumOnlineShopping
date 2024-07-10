from flask import Blueprint, render_template, redirect, url_for, flash,request
from config import get_cursor
from ..controllers.user_controllers import get_session_info, login_required
from ..models.order_model import get_orders, get_order_info, get_order_sum
import math

# SCRUM-8 customer track order and payment by Danfeng
customer_track_order = Blueprint(
    'customer_track_order',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# create a route to display the user's orders
@customer_track_order.route('/', methods=['GET'])
def list_order():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login and (role_id == 1 or role_id == 2):
        page = request.args.get('page', 1, type=int)
        per_page = 8
        
        all_orders = get_orders(user_id)
        total_orders = len(all_orders)
        
        # Pagination calculations
        total_pages = math.ceil(total_orders / per_page)
        offset = (page - 1) * per_page
        
        paginated_orders = all_orders[offset:offset + per_page]

        return render_template(
            '/customer_track_order/list_all_orders.html',
            all_orders=paginated_orders,
            page=page,
            total_pages=total_pages
        )
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))

    
# the customer view the detail of an order
@customer_track_order.route('/view_order/<int:order_id>', methods=['GET'])
@login_required    
def view_order(order_id):
    is_login, user_id, role_id,discount_rate = get_session_info()
    order_detail = []
    order_sum = []
    if is_login ==True and (role_id==1 or role_id==2):
        order_detail = get_order_info(order_id) 
        order_sum = get_order_sum(order_id) 
        return render_template('/customer_track_order/customer_view_order.html',order_id = order_id, order_detail = order_detail, order_sum = order_sum)
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))

    
# the user view receipt   
@customer_track_order.route('/view_receipt/<int:current_order_id>', methods=['GET'])
def view_receipt(current_order_id):
    is_login, user_id, role_id,discount_rate = get_session_info()
    if is_login ==True and (role_id==1 or role_id==2):
        try:
            cursor = get_cursor()
            cursor.execute("SELECT total_incl_gst, shipping_fee, total_amount, payment_date, type_name FROM invoices JOIN payments ON invoices.id=payments.invoice_id JOIN payment_types ON payments.payment_type_id=payment_types.id WHERE order_id=%s",(current_order_id,))
            receipt = cursor.fetchone()                
        except Exception as e:
            print(f"An error occurred: {e}")  
            flash('An error occurred. Please try again later.', 'danger')
        return render_template('/customer_track_order/view_receipt.html', receipt=receipt)
    else:  
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))

  