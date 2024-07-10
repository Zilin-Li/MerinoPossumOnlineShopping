from flask import Blueprint, render_template, redirect, url_for, flash, session
from config import get_cursor
from ..controllers.user_controllers import get_session_info


# SCRUM-32 Manager run a sales trend report by Danfeng
sales_trend_report = Blueprint(
    'sales_trend_report',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# create a route to display the user's orders
@sales_trend_report.route('/', methods=['GET'])
def sales_report():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        all=[]
        try:
            all_sql = """
                SELECT YEAR(order_date) as year, MONTH(order_date) as month, SUM(total_excl_gst) as total_consumption
                FROM orders o
                WHERE order_date > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 12 MONTH), '%Y-%m-01')
                GROUP BY YEAR(order_date), MONTH(order_date)
                ORDER BY YEAR(order_date), MONTH(order_date)
                    """
            cursor = get_cursor()
            cursor.execute(all_sql)
            all = cursor.fetchall()                   
        except Exception as e:
            print(f"An error occurred: {e}")  
            flash('An error occurred. Please try again later.', 'danger')

        time=[]
        all_consumption=[]
        for row in all:
            month_year = str(row[1])+"/"+str(row[0])
            time.append(month_year)
            all_consumption.append(row[2])
        try:
            customer_sql = """
                SELECT YEAR(order_date) as year, MONTH(order_date) as month, SUM(total_excl_gst) as total_consumption
                FROM orders o
                JOIN users u ON o.user_id = u.id
                JOIN roles r ON u.role_id = r.id
                WHERE order_date > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 12 MONTH), '%Y-%m-01') AND role_id=1
                GROUP BY YEAR(order_date), MONTH(order_date)
                ORDER BY YEAR(order_date), MONTH(order_date)
                    """
            cursor = get_cursor()
            cursor.execute(customer_sql)
            customer = cursor.fetchall()                 
        except Exception as e:
            print(f"An error occurred: {e}")  
            flash('An error occurred. Please try again later.', 'danger')

        customer_consumption=[]
        for row in customer:            
            customer_consumption.append(row[2])
        try:
            client_sql = """
                SELECT YEAR(order_date) as year, MONTH(order_date) as month, SUM(total_excl_gst) as total_consumption
                FROM orders o
                JOIN users u ON o.user_id = u.id
                JOIN roles r ON u.role_id = r.id
                WHERE order_date > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 12 MONTH), '%Y-%m-01') AND role_id=2
                GROUP BY YEAR(order_date), MONTH(order_date)
                ORDER BY YEAR(order_date), MONTH(order_date)
                    """
            cursor = get_cursor()
            cursor.execute(client_sql)
            client = cursor.fetchall()                  
        except Exception as e:
            print(f"An error occurred: {e}")  
            flash('An error occurred. Please try again later.', 'danger')
        client_consumption=[]
        for row in client:            
            client_consumption.append(row[2])
        return render_template('/sales_trend_report/sales_trend_report.html', time=time, all_consumption=all_consumption, customer_consumption=customer_consumption, client_consumption=client_consumption )
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))