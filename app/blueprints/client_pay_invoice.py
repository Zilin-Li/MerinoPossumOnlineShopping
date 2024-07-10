from flask import Blueprint, render_template, redirect, url_for, request, flash
from config import get_cursor
from ..controllers.user_controllers import get_session_info
from ..models.order_model import get_order_info, get_order_sum
import json
from decimal import Decimal
import math

# SCRUM-82 a Corporate Client pay invoices by Danfeng
client_pay_invoice = Blueprint(
    'client_pay_invoice',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# This function converts Decimal objects to strings for JSON serialization.
def serialize_invoice_list(invoice_list):
    serialized_list = []
    for invoice in invoice_list:
        serialized_invoice = [str(item) if isinstance(item, Decimal) else item for item in invoice]
        serialized_list.append(serialized_invoice)
    return json.dumps(serialized_list)

# the client displays all unpaid invoices 
@client_pay_invoice.route('/', methods=['GET'] )
def display_invoice():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if role_id != 2:
        return redirect(url_for('users.login'))
    else:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        invoice_list = []
        cursor = get_cursor()
        try:
            sql_count = """
                SELECT COUNT(*) 
                FROM invoices 
                WHERE user_id=%s AND is_paid=0
            """
            cursor.execute(sql_count, (user_id,))
            total_invoices = cursor.fetchone()[0]

            total_pages = math.ceil(total_invoices / per_page)
            offset = (page - 1) * per_page

            sql = """
                SELECT id, order_id, total_incl_gst, shipping_fee, total_amount
                FROM invoices 
                WHERE user_id=%s AND is_paid=0
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (user_id, per_page, offset))
            invoice_list = cursor.fetchall()
            serialized_invoice_list = serialize_invoice_list(invoice_list)
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred. Please try again later.', 'danger')
        
        return render_template(
            '/client_pay_invoice/client_view_invoice.html',
            serialized_invoice_list=serialized_invoice_list,
            invoice_list=invoice_list,
            page=page,
            total_pages=total_pages
        )

# the client chooses to pay all unpaid invoices    
@client_pay_invoice.route('/display_payment_page_all', methods=['POST'])
def display_payment_page_all():
    is_login, user_id, role_id, discount_rate = get_session_info()
    total = 0
    if role_id != 2:
        return redirect(url_for('users.login'))
    else:
        invoice_list_json = request.form.get('invoice_list')
        if invoice_list_json:
            try:
                invoice_list = json.loads(invoice_list_json)
                total = sum(Decimal(invoice[4]) for invoice in invoice_list if len(invoice) > 4)
                serialized_invoice_list = serialize_invoice_list(invoice_list)
            except Exception as e:
                print(f"An error occurred: {e}")  
                flash('An error occurred. Please try again later.', 'danger') 
                        
        return render_template('client_pay_invoice/client_payment_page_all.html', invoice_list = invoice_list, total = total, serialized_invoice_list = serialized_invoice_list )

# update the database after the client pays all unpaid invoices    
@client_pay_invoice.route('/confirm_payment_all', methods=['POST'])
def confirm_payment_all():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if role_id != 2:
        return redirect(url_for('users.login'))
    else:
        invoice_list_json = request.form.get('invoice_list')
        if invoice_list_json:
            try:
                invoice_list = json.loads(invoice_list_json)                
                cursor = get_cursor()
                for invoice in invoice_list:
                    cursor.execute("UPDATE invoices SET is_paid = %s WHERE id = %s", (1, invoice[0]))
                    cursor.execute('INSERT INTO payments (user_id, invoice_id, payment_date, payment_type_id) VALUES (%s, %s, NOW(), %s)', (user_id, invoice[0], 1))
                    cursor.execute("SELECT total_amount FROM invoices WHERE id = %s", (invoice[0],))
                    total_amount = cursor.fetchone()[0]
                    cursor.execute("UPDATE corporate_clients SET available_credit = available_credit+ %s WHERE user_id = %s", (total_amount, user_id))
                flash(f'Payment has been made', 'success')
            except Exception as e:
                    print(f"An error occurred: {e}")
                    flash('An error occurred. Please try again later.', 'danger')      
        return redirect(url_for('client_pay_invoice.display_invoice'))
    

# the client view the detail of an order
@client_pay_invoice.route('/view_order/<int:order_id>', methods=['GET'])  
def view_order(order_id):
    is_login, user_id, role_id, discount_rate = get_session_info()
    order_detail = []
    order_sum = []
    if role_id != 2:
        return redirect(url_for('users.login'))
    else:
        order_detail = get_order_info(order_id) 
        order_sum = get_order_sum(order_id) 
        return render_template('/client_pay_invoice/client_view_order.html',order_id = order_id, order_detail = order_detail, order_sum = order_sum)

# the client chooses to pay a specific unpaid invoice 
@client_pay_invoice.route('/display_payment_page/<int:invoice_id>')
def display_payment_page(invoice_id):
    is_login, user_id, role_id, discount_rate = get_session_info()
    invoice = []
    if role_id != 2:
        return redirect(url_for('users.login'))
    else:
        try:
            cursor = get_cursor()
            cursor.execute("SELECT id, order_id, total_amount FROM invoices WHERE id = %s", (invoice_id,))
            invoice = cursor.fetchone()
        except Exception as e:
            print(f"An error occurred: {e}")  
            flash('An error occurred. Please try again later.', 'danger') 

        return render_template('client_pay_invoice/client_payment_page.html', invoice = invoice)

# update the database after the client pays a specific unpaid invoice
@client_pay_invoice.route('/confirm_payment/<int:invoice_id>', methods=['POST'])
def confirm_payment(invoice_id):
    is_login, user_id, role_id, discount_rate = get_session_info()
    if role_id != 2:
        return redirect(url_for('users.login'))
    else:
        try:
            cursor = get_cursor()
            cursor.execute("UPDATE invoices SET is_paid = %s WHERE id = %s", (1, invoice_id))
            cursor.execute('INSERT INTO payments (user_id, invoice_id, payment_date, payment_type_id) VALUES (%s, %s, NOW(), %s)', (user_id, invoice_id, 1))
            cursor.execute("SELECT total_amount FROM invoices WHERE id = %s", (invoice_id,))
            total_amount = cursor.fetchone()[0]
            cursor.execute("UPDATE corporate_clients SET available_credit = available_credit+ %s WHERE user_id = %s", (total_amount, user_id))
            flash(f'Payment of invoice {invoice_id} has been made', 'success')
        except Exception as e:
                print(f"An error occurred: {e}")
                flash('An error occurred. Please try again later.', 'danger')      

        return redirect(url_for('client_pay_invoice.display_invoice'))

