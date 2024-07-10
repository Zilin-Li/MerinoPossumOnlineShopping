from flask import Blueprint, render_template, redirect, url_for, flash, session
from config import get_cursor
from ..controllers.user_controllers import get_session_info


# SCRUM-65 Manager run a customer demographics report by Danfeng
customer_demographics_report = Blueprint(
    'customer_demographics_report',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# create a route to display the user's orders
@customer_demographics_report.route('/', methods=['GET'])
def display_report():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        distribution=[]
        try:
            cursor = get_cursor()
            cursor.execute("SELECT country, count(id) FROM users WHERE role_id=1 AND is_active=1 GROUP BY country")
            distribution = cursor.fetchall()                   
        except Exception as e:
            print(f"An error occurred: {e}")  
            flash('An error occurred. Please try again later.', 'danger')

        country = []
        population = []
        for row in distribution:
            country.append(row[0])
            population.append(row[1])
        return render_template('/customer_demographics_report/customer_demographics_report.html', country = country, population = population )
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))