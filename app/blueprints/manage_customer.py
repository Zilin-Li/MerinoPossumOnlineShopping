from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from config import get_cursor
from ..controllers.user_controllers import get_session_info, check_user_exists_by_email, check_user_exists_by_username, check_password
from werkzeug.security import generate_password_hash
import re

import math

# SCRUM-29 Manager manage customer by Danfeng
manage_customer = Blueprint(
    'manage_customer',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# manager or administrator display all customers
@manage_customer.route('/')
def display_all_customers():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login and (session.get('is_manager') == 1 or session.get('is_admin') == 1):
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        customer_list = []
        cursor = get_cursor()
        try:
            # Get the total number of customers
            sql_count = """
                SELECT COUNT(*)
                FROM users 
                WHERE role_id = 1
            """
            cursor.execute(sql_count)
            total_customers = cursor.fetchone()[0]

            total_pages = math.ceil(total_customers / per_page)
            offset = (page - 1) * per_page

            # Get the paginated customers
            query = """
                SELECT id, username, email, first_name, last_name, phone, country, is_active
                FROM users 
                WHERE role_id = 1 
                ORDER BY first_name, last_name
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (per_page, offset))
            customer_list = cursor.fetchall()
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
        
        return render_template(
            '/manage_customer/display_all_customers.html',
            customer_list=customer_list,
            page=page,
            total_pages=total_pages
        )
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 

# manager or administrator view and edit a specific customer
@manage_customer.route('/edit_customer/<int:customer_id>', methods=['GET','POST'])
def edit_customer(customer_id):
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        if request.method == 'POST':
            email = request.form.get('email', '')
            first_name = request.form.get('first_name', '')
            last_name = request.form.get('last_name', '')
            phone = request.form.get('phone', '')
            street_address = request.form.get('street_address', '')
            city = request.form.get('city', '')
            state = request.form.get('state', '')
            country = request.form.get('country', '')
            post_code = request.form.get('post_code', '')
            is_active =request.form.get('is_active')
            
            if email and not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!','error')
                return redirect(url_for('manage_customer.edit_customer', customer_id = customer_id))
            try:    
                cursor = get_cursor() 
                update_customer_query = "UPDATE users SET email = %s, first_name = %s, last_name = %s, phone = %s, street_address = %s, city = %s, state = %s, country = %s, post_code = %s, is_active = %s WHERE id = %s"
                cursor.execute(update_customer_query, (email, first_name, last_name, phone, street_address, city, state, country, post_code, is_active, customer_id ))
                flash('Update the customer successfully', 'success')
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')

        query = """
            SELECT id, username, email, first_name, last_name, phone, street_address, city, state, country, post_code, is_active
            FROM users 
            WHERE id = %s """       
        customer_detail = []
        try:
            cursor = get_cursor()
            cursor.execute(query, (customer_id,))
            customer_detail = cursor.fetchone()  
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
  
        return render_template('/manage_customer/edit_customer.html', customer_detail = customer_detail)  
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 

# manager or administrator add a new customer
@manage_customer.route('/add_customer', methods=['GET','POST'])
def add_customer():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        if request.method == 'POST':
            username= request.form.get('username')
            is_active =request.form.get('is_active') 
            email = request.form.get('email')
            password=request.form.get('password')
            confirm_password= request.form.get('confirm_password')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')

            phone = request.form.get('phone', '')
            street_address = request.form.get('street_address', '')
            city = request.form.get('city', '')
            state = request.form.get('state', '')
            country = request.form.get('country', '')
            post_code = request.form.get('post_code', '')
            
            # check if all fields are filled
            if not (username and first_name and last_name and email and password and confirm_password):
                flash('Please fill all fields.', 'error')
                return render_template('/manage_customer/add_customer.html')

            # check if the username is already registered
            if check_user_exists_by_username(username):
                flash('Username already registered, you can sign in directly.', 'error')
                return render_template('/manage_customer/add_customer.html')

            # check if the email is already registered
            if check_user_exists_by_email(email):
                flash('Email already registered, you can sign in directly.', 'error')
                return render_template('/manage_customer/add_customer.html')

            # check if the passwords match
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('/manage_customer/add_customer.html')

            # check if the password is strong
            if not check_password(password):
                flash('Password is not strong.', 'error')
                return render_template('/manage_customer/add_customer.html')

            # hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                  
            cursor = get_cursor()
            try:  
                cursor.execute(
                    "INSERT INTO users (username, email, hashed_password, first_name, last_name, phone, street_address, city, state, country, post_code, is_active, role_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (username, email, hashed_password, first_name, last_name, phone, street_address, city, state, country, post_code, is_active, 1)
                )
                user_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO customers (user_id, point) VALUES (%s, %s)", (user_id, 0)
                )
                flash(
                    'Congratulations, your have added a customer account successfully.🎉🎉🎉', 'success')
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')  

        return render_template('/manage_customer/add_customer.html')
    
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 
