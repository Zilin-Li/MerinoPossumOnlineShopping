from flask import Blueprint, render_template, redirect, url_for, request, flash
from config import get_cursor
from ..controllers.user_controllers import get_session_info
import datetime

# SCRUM-23 Staff Member view a daily summary of orders by Danfeng
daily_orders_summary = Blueprint(
    'daily_orders_summary',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# create a route to display daily summary of orders
@daily_orders_summary.route('/')
def display_summary():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login == False or role_id != 3:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))
    else:   
        date = request.args.get('date')

        query1 = """
            SELECT count( DISTINCT o.id), sum(quantity)
            FROM orders o
            JOIN order_details od ON o.id = od.order_id         
        """
        query2 = """
            SELECT DISTINCT delivery_country
            FROM orders          
        """
        query3 = """
            SELECT product_name, sum(quantity)
            FROM orders o
            JOIN order_details od ON o.id = od.order_id
            JOIN product_variants pv ON od.variant_id = pv.id
            JOIN products p ON pv.product_id = p.id 

        """
        query4 = """
            SELECT  delivery_city, delivery_state, delivery_country, count(id)
            FROM orders       
        """
        params = []

        if date:
            try:
                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                query1 += " WHERE order_date = %s"
                query2 += " WHERE order_date = %s"
                query3 += " WHERE order_date = %s"
                query4 += " WHERE order_date = %s"
                params.append(date)
            except ValueError:
                flash("The date provided is invalid.", "error")  # Handle invalid date format

        query3 += " GROUP BY p.id"
        query4 += " GROUP BY delivery_city, delivery_state, delivery_country"

        summary = []
        country_list = []
        item_list = []
        address_list = []

        dbconn = get_cursor()
        try:
            dbconn.execute(query1, tuple(params))
            summary = dbconn.fetchone()
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred. Please try again later.', 'danger')   
        try:
            dbconn.execute(query2, tuple(params))
            country_list = dbconn.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred. Please try again later.', 'danger')  
        try:
            dbconn.execute(query3, tuple(params))
            item_list = dbconn.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred. Please try again later.', 'danger')     
        try:
            dbconn.execute(query4, tuple(params))
            address_list = dbconn.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred. Please try again later.', 'danger')        
        
        return render_template('/staff/daily_orders_summary.html', summary = summary, country_list = country_list, item_list = item_list, address_list = address_list )  