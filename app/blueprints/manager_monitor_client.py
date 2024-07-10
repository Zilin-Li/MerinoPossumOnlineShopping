from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from config import get_cursor
from ..controllers.user_controllers import get_session_info, login_required
from ..models.order_model import get_order_info, get_order_sum
import math


# SCRUM-50 and SCRUM-51 manager monitor client monthly account outstanding balances by Danfeng
manager_monitor_client = Blueprint(
    'manager_monitor_client',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# manager displays client account outstanding balances
@manager_monitor_client.route('/',methods=['GET','POST'] )
def display_account():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login and (session.get('is_manager') == 1 or session.get('is_admin') == 1):
        if request.method == 'POST':
            outstanding_balance = request.form.get('outstanding_balance', '')
            receive_id = request.form.get('receive_id', '')           
            try:    
                cursor = get_cursor()                 
                message_content = f'Hi there! Your outstanding balance is {outstanding_balance} NZD. Payments can be made under My Invoices on your Dashboard.'
                cursor.execute("INSERT INTO messages (send_id, receive_id, message_content, message_type_id) VALUES (%s, %s, %s, %s)",
                            (user_id, receive_id, message_content, 2))
                flash(f'Reminder sent to client with ID {receive_id}', 'success')
            except Exception as e:
                print(f"An error occurred: {e}")
                flash('An error occurred. Please try again later.', 'danger')

        name = request.args.get('name')
        phone = request.args.get('phone')
        page = request.args.get('page', 1, type=int)
        per_page = 10

        query = """
            SELECT u.id, company_name, phone, credit_limit, available_credit, 
                   COALESCE((SELECT SUM(total_amount) FROM invoices WHERE is_paid = 0 AND user_id = u.id), 0) AS outstanding_balance
            FROM users u
            JOIN corporate_clients cc ON u.id = cc.user_id
            WHERE 1=1
        """
        params = []

        if name:
            query += " AND company_name LIKE %s"
            params.append(f"%{name}%")

        if phone:
            query += " AND phone LIKE %s"
            params.append(f"%{phone}%")
            
        query += " ORDER BY outstanding_balance DESC"

        client_list = []
        dbconn = get_cursor()
        try:
            # Get the total number of clients
            sql_count = f"SELECT COUNT(*) FROM ({query}) AS total"
            dbconn.execute(sql_count, tuple(params))
            total_clients = dbconn.fetchone()[0]

            total_pages = math.ceil(total_clients / per_page)
            offset = (page - 1) * per_page

            # Get the paginated clients
            paginated_query = query + " LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            dbconn.execute(paginated_query, tuple(params))
            client_list = dbconn.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred. Please try again later.', 'danger')

        if phone and not client_list:
            flash("No clients found for the phone number.", "error")

        if name and not client_list:
            flash("No clients found for the name.", "error")
        
        return render_template(
            '/manager_monitor_client/manager_display_outstanding_balance.html',
            client_list=client_list,
            page=page,
            total_pages=total_pages
        )
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))

# the manager view the unpaid invoices of a corporate client
@manager_monitor_client.route('/view_invoice/<int:u_id>', methods=['GET'])
@login_required    
def view_invoice(u_id):
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        invoice_detail = []
        cursor = get_cursor()        
        try:
            sql="""
                SELECT id, order_id, total_incl_gst, shipping_fee, total_amount, user_id
                FROM invoices 
                WHERE user_id=%s AND is_paid=0
            """
            cursor.execute(sql, (u_id,))
            invoice_detail = cursor.fetchall()                 
        except Exception as e:
            print(f"An error occurred: {e}")  
            flash('An error occurred. Please try again later.', 'danger')     
        return render_template('/manager_monitor_client/manager_view_invoice.html', invoice_detail = invoice_detail)
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 

# the manager view the detail of an order
@manager_monitor_client.route('/view_order/<int:order_id>', methods=['GET'])
@login_required    
def view_order(order_id):
    is_login, user_id, role_id, discount_rate = get_session_info()
    order_detail = []
    order_sum = []
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        order_detail = get_order_info(order_id) 
        order_sum = get_order_sum(order_id) 
        return render_template('/manager_monitor_client/manager_view_order.html',order_id = order_id, order_detail = order_detail, order_sum = order_sum)
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 

