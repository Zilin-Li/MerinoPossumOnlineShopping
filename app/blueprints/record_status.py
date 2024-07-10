from flask import Blueprint, render_template, redirect, url_for, request, flash
from config import get_cursor
from ..controllers.user_controllers import get_session_info, login_required
from ..models.order_model import get_order_info, get_order_sum
import math


# SCRUM-22 staff record status by Danfeng
staff_record_status = Blueprint(
    'staff_record_status',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# staff displays orders and change status
@staff_record_status.route('/',methods=['GET','POST'] )
def display_orders():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if not is_login or role_id != 3:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))
    else:
        if request.method == 'POST':
            order_id = request.form.get('order_id', '')
            status_id = request.form.get('status_id', '')
            receive_id = request.form.get('receive_id', '')           
            try:
                cursor = get_cursor() 
                cursor.execute("UPDATE orders SET status_id = %s WHERE id = %s", (status_id, order_id))
                flash('Update status successfully', 'success')
                cursor.execute("SELECT status_type FROM order_status_types WHERE id = %s", (status_id,))
                status_type = cursor.fetchone()[0]
                message_content = f'Good news! The status of your order {order_id} has been changed. Its current status is: {status_type}. More info available under My Orders on your Dashboard.'
                cursor.execute("INSERT INTO messages (send_id, receive_id, message_content, message_type_id) VALUES (%s, %s, %s, %s)",
                            (user_id, receive_id, message_content, 2))
            except Exception as e:
                print(f"An error occurred: {e}")
                flash('An error occurred. Please try again later.', 'danger')
    
        name = request.args.get('name')
        phone = request.args.get('phone')
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        query = """
            SELECT orders.id, order_date, total_amount, recipient_name, recipient_mobile, status_id, orders.user_id 
            FROM orders 
            JOIN invoices on orders.id=invoices.order_id
            WHERE 1=1
        """
        params = []

        if name:
            query += " AND recipient_name LIKE %s"
            params.append(f"%{name}%")

        if phone:
            query += " AND recipient_mobile LIKE %s"
            params.append(f"%{phone}%")
            
        query += " ORDER BY order_date DESC, status_id"
        
        # Pagination calculations
        offset = (page - 1) * per_page
        
        paginated_query = query + " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        order_list = []
        total_orders = 0
        dbconn = get_cursor()
        try:
            # Get the total number of orders
            dbconn.execute(f"SELECT COUNT(*) FROM ({query}) AS total", tuple(params[:-2]))
            total_orders = dbconn.fetchone()[0]
            
            # Get the paginated orders
            dbconn.execute(paginated_query, tuple(params))
            order_list = dbconn.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred. Please try again later.', 'danger')
        
        total_pages = math.ceil(total_orders / per_page)

        if phone and not order_list:
            flash("No orders found for the phone number.", "error")

        if name and not order_list:
            flash("No orders found for the name.", "error")
        
        return render_template('/staff_record_status/staff_record_status.html', order_list=order_list, page=page, total_pages=total_pages)


# the staff view the detail of an order
@staff_record_status.route('/view_order/<int:order_id>', methods=['GET'])
@login_required    
def view_order(order_id):
    is_login, user_id, role_id, discount_rate = get_session_info()
    order_detail = []
    order_sum = []
    if role_id != 3:
        return redirect(url_for('users.login'))
    else:
        order_detail = get_order_info(order_id) 
        order_sum = get_order_sum(order_id) 
        return render_template('/staff_record_status/staff_view_order.html',order_id = order_id, order_detail = order_detail, order_sum = order_sum)

