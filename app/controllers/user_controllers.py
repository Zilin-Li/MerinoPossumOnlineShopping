from functools import wraps
from ..models import user_model
from config import get_cursor
from flask import flash, redirect, session, url_for


# check if user exists by email
def check_user_exists_by_email(email):
    # connect to database and get cursor
    dbconn = get_cursor()
    # query the database
    try:
        dbconn.execute(
            "SELECT * FROM users WHERE email = %s", (email,))
        user = dbconn.fetchone()

        return user
    except Exception as e:
        print('An error occurred: ' + str(e))
        return False

# check if user exists by username


def check_user_exists_by_username(username):
    # connect to database and get cursor
    dbconn = get_cursor()
    # query the database
    try:
        dbconn.execute(
            "SELECT * FROM users WHERE username = %s", (username,))
        user = dbconn.fetchone()

        return user
    except Exception as e:
        print('An error occurred: ' + str(e))
        return False

# check if the password is secure


def check_password(password):
    # check if the password is at least 8 characters long
    if len(password) < 8:
        flash('Password must be at least 8 characters long', 'danger')
    # check if password does not contain any numbers
    elif not any(char.isdigit() for char in password):
        flash('Password must contain at least one number', 'danger')
    # check if password does not contain any uppercase characters
    elif not any(char.isupper() for char in password):
        flash('Password must contain at least one uppercase character', 'danger')
    # check if password does not contain any lowercase characters
    elif not any(char.islower() for char in password):
        flash('Password must contain at least one lowercase character', 'danger')
    # check if password does not contain any special characters
    elif not any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?`~' for char in password):
        flash('Password must contain at least one special character', 'danger')
        return False
    else:
        return True


# create a decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You must be logged in to access this page.⛔️', 'danger')
            return redirect(url_for('users.login'))
        return f(*args, **kwargs)
    return decorated_function


# create a decorator to prevent the user from accessing the page if they are logged in
def prevent_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            flash('You are already logged in.✋', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def get_session_info():
   # get the session information, if the user is not logged in, return False, None, '', None
   # otherwise, return True, user_id, username, role_id
    is_login = session.get('logged_in', False)
    user_id = session.get('user_id', None)
    role_id = session.get('role_id', None)
    discount_rate = session.get('discount_rate', 0)
    return is_login, user_id, role_id, discount_rate

# get user's gift card information
def  get_gift_card_info(user_id):
    """
    Get user's gift cards information by user id
    """
    return user_model. get_gift_card_info(user_id) 

