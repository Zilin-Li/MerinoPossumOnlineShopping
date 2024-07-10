import re
from config import get_cursor
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..controllers.user_controllers import check_user_exists_by_email, check_user_exists_by_username, check_password, prevent_login, get_session_info
from ..controllers.forms import RegistrationForm, LoginForm, ClientRegistrationForm

users = Blueprint(
    'users',
    __name__,
    static_folder='static',
    template_folder='templates'
)


@users.route('/register', methods=['GET', 'POST'])
@prevent_login
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        # check if all fields are filled
        if not (username and first_name and last_name and email and password and confirm_password):
            flash('Please fill all fields.', 'error')
            return redirect(url_for('users.register'))

        # check if the email is already registered
        if check_user_exists_by_email(email):
            flash('Email already registered, you can sign in directly.', 'error')
            return redirect(url_for('users.login'))

        # check if the passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('users.register'))

        # check if the password is strong
        if not check_password(password):
            flash('Password is not strong.', 'error')
            return redirect(url_for('users.register'))

        # hash the password
        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=8)

        # connect to database
        dbconn = get_cursor()

        # execute the query
        try:  
            dbconn.execute(
                "INSERT INTO users (username, first_name, last_name, email, hashed_password, role_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, first_name, last_name, email, hashed_password, 1)
            )
            user_id = dbconn.lastrowid
            dbconn.execute(
                "INSERT INTO customers (user_id, point) VALUES (%s, %s)",
                (user_id, 0)
            )
            flash(
                'Congratulations, your account has been registered successfully.🎉🎉🎉', 'success')
            return redirect(url_for('users.login'))
        except Exception as e:
           
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('users.register'))

    return render_template('users/user_register.html', form=form)


@users.route('/login', methods=['GET', 'POST'])
@prevent_login
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # get the form data
        username_or_email = form.username_or_email.data
        password = form.password.data

        # check if all fields are filled
        if not (username_or_email and password):
            flash('Please fill all fields', 'error')
            return redirect(url_for('users.login'))

        # check what is the user input
        if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", username_or_email):
            email = username_or_email
            user_infors = check_user_exists_by_email(email)
        else:
            username = username_or_email
            user_infors = check_user_exists_by_username(username)

        if user_infors is None:
            flash('You account does not exist, please register first', 'error')
            return redirect(url_for('users.register'))
        else:
            # check if user's password is correct
            if not check_password_hash(user_infors[3], password):
                flash('Invalid password, please try again', 'error')
                return redirect(url_for('users.login'))
            else:
                discount_rate = 1
                #check if the user is a corporate client
                if user_infors[13] == 2:
                    #check if the client get the approval from the manager
                    dbconn = get_cursor()
                    dbconn.execute("SELECT is_approved FROM corporate_clients WHERE user_id = %s", (user_infors[0],))
                    is_approved = dbconn.fetchone()
                    is_approved = is_approved[0] if is_approved else 0
                    if is_approved == 1:
                        #get the client's discount rate
                        dbconn.execute("SELECT discount_level FROM corporate_clients WHERE user_id = %s", (user_infors[0],))
                        discount_level = dbconn.fetchone()
                        if discount_level is not None:
                            discount_level_value = discount_level[0]
                            # Calculate the discount multiplier based on the discount level
                            if discount_level_value != 0:
                                discount_rate = 1 - (discount_level_value * 0.10)
                       
                        # Default discount multiplier if no discount level is found
                is_manager = 0
                is_admin = 0
                if user_infors[13] == 3:
                    try:
                        dbconn = get_cursor()
                        dbconn.execute("SELECT is_manager, is_admin FROM employees WHERE user_id = %s", (user_infors[0],))
                        employee=dbconn.fetchone()
                        is_manager = employee[0]
                        is_admin = employee[1]
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        flash('An error occurred. Please try again later.', 'danger') 
                    finally:
                        dbconn.close() 

                session['is_manager'] = is_manager
                session['is_admin'] = is_admin
                session['discount_rate'] = str(discount_rate)
                        
                # create a session for the user
                session['user_id'] = user_infors[0]
                session['username'] = user_infors[1]
                session['email'] = user_infors[2]
                session['first_name'] = user_infors[4]
                session['last_name'] = user_infors[5]
                session['role_id'] = user_infors[13]
                session['logged_in'] = True

                return redirect(url_for('home'))

    return render_template('users/user_login.html', form=form)


@users.route('/logout')
def logout():
    # clean all session
    session.clear()
    flash('Logout successful, see you soon. 👋👋👋', 'success')
    return redirect(url_for('users.login'))


# @users.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template('users/dashboard.html')

# SCRUM-15 corporate client register by Danfeng
@users.route('/corporate_client_register', methods=['GET', 'POST'])
@prevent_login
def corporate_client_register():
    form = ClientRegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        company_name = form.company_name.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        # check if all fields are filled
        if not (username and company_name and first_name and last_name and email and password and confirm_password):
            flash('Please fill all fields.', 'error')
            return redirect(url_for('users.corporate_client_register'))

        # check if the username is already registered
        if check_user_exists_by_username(username):
            flash('Username already registered, you can sign in directly.', 'error')
            return redirect(url_for('users.login'))

        # check if the email is already registered
        if check_user_exists_by_email(email):
            flash('Email already registered, you can sign in directly.', 'error')
            return redirect(url_for('users.login'))

        # check if the passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('users.register'))

        # check if the password is strong
        if not check_password(password):
            flash('Password is not strong.', 'error')
            return redirect(url_for('users.register'))

        # hash the password
        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=8)

        # connect to database
        dbconn = get_cursor()

        # execute the query
        try:
            dbconn.execute(
                "INSERT INTO users (username, first_name, last_name, email, hashed_password, role_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, first_name, last_name, email, hashed_password, 2)
            )
            # Fetch the user_id of the newly created user
            dbconn.execute(
                "SELECT id from users WHERE username=%s",
                (username, )
            )
            user_id=dbconn.fetchone()[0]
            dbconn.execute(
                "INSERT INTO corporate_clients (user_id, company_name, is_approved, discount_level, credit_limit, available_credit) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, company_name, 0, 0, 0.00, 0.00)
            )
            flash(
                'Congratulations, your account has been registered successfully.🎉🎉🎉 Your discount rate and available credit will be decided and approved by manager soon', 'success')
            return redirect(url_for('users.login'))
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('users.corporate_client_register'))

    return render_template('users/corporate_client_register.html', form=form)

# SCRUM-33 manager approve pending corporate client applications by Danfeng
@users.route('/manager_approve_pending_corporate_client',methods=['GET','POST'] )
def manager_approve_pending_corporate_client():
    is_login, user_id, role_id, discount_rate = get_session_info()
    pending_corporate_client_list = []
    if is_login == False or user_id != 3:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))
    else:
        if request.method == 'POST':
            # get the form data
            id=request.form.get('id', '')
            receive_id=request.form.get('receive_id', '')
            discount_level= int(request.form.get('discount_level', ''))
            credit_limit= request.form.get('credit_limit', '')
            try:    
                cursor = get_cursor() 
                cursor.execute("UPDATE corporate_clients SET is_approved=%s, discount_level=%s, credit_limit=%s, available_credit=%s WHERE id=%s", 
                               (1, discount_level, credit_limit, credit_limit, id))
                
                if discount_level == 0:
                    discount = '0% Off'
                elif discount_level == 1:
                    discount = '10% Off'
                elif discount_level == 2:
                    discount = '20% Off'
                elif discount_level == 3:
                    discount = '30% Off'
                elif discount_level == 4:
                    discount = '40% Off'
                else:
                    discount = '50% Off'
                message_content = 'Congratulations! Your account is approved. \nYour discount level is: '+discount+'. \nYour credit limit is: '+str(credit_limit)+' NZD.\n Please log in again to view your discount.'
                cursor.execute("INSERT INTO messages (send_id, receive_id, message_content, message_type_id)  VALUES (%s, %s, %s, %s)",
                               (user_id, receive_id, message_content, 1))
                flash('Approve client successfully', 'success')
            except Exception as e:
                print(f"An error occurred: {e}")
                flash('An error occurred. Please try again later.', 'danger')          
    try:
        cursor = get_cursor()
        cursor.execute("SELECT * FROM corporate_clients WHERE is_approved=0")
        pending_corporate_client_list = cursor.fetchall()                    
    except Exception as e:
        print(f"An error occurred: {e}")  
        flash('An error occurred. Please try again later.', 'danger')               
    return render_template('/messages/manager_approve_pending_corporate_client.html',pending_corporate_client_list = pending_corporate_client_list)       

