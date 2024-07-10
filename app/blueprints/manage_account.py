from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..models.manage_account_model import get_a_user,get_an_employee
from ..controllers.user_controllers import check_password, get_session_info, login_required
from config import get_cursor
from werkzeug.security import generate_password_hash, check_password_hash


# Scrum 42, 27, 47, 35 by Danfeng
manage_account = Blueprint(
    'manage_account',
    __name__,
    static_folder='static',
    template_folder='templates'
)


# create a route to display the user profile
@manage_account.route('/', methods=['GET'])
@login_required
def user_profile():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if role_id!=3:
        user = get_a_user(user_id)
        date=None
    else:
        user=get_an_employee(user_id)
        date = user[10].strftime("%d-%m-%Y")            
    return render_template('/manage_account/profile.html', user=user, role_id=role_id, date=date)



# create a route to edit the user profile
@manage_account.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_user_profile():
    is_login, user_id, role_id, discount_rate = get_session_info()  
    if request.method == 'POST':
        # get the form data
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        street_address = request.form['street_address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        post_code = request.form['post_code']
        
        cursor = get_cursor()
        try:
            cursor.execute("UPDATE users SET email=%s, first_name=%s, last_name=%s, phone=%s, street_address=%s, city=%s, state=%s,country=%s,post_code=%s WHERE id=%s;",
                        (email, first_name, last_name, phone, street_address, city, state, country, post_code, user_id))
            flash('Update profile successfully', 'success')
        except Exception as e:
            print('An error occurred: ' + str(e))
            flash('An error occurred. Please try again later.', 'danger') 

    user = get_a_user(user_id)
    return render_template('/manage_account/edit_profile.html', user=user)

# create a route to change the user password
@manage_account.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    is_login, user_id, role_id, discount_rate = get_session_info()
    # check if the request method is POST
    if request.method == 'POST':
        if 'current_password' not in request.form or 'new_password' not in request.form or 'confirm_password' not in request.form:
            # flash a message to the user
            flash('Please fill in all the fields', 'error')
            return redirect(url_for('manage_account.change_password'))
        else:
            # get the form data
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            # check if the new password and confirm password are the same
            if new_password != confirm_password:
                flash('Password does not match', 'error')
                return redirect(url_for('manage_account.change_password'))
            else:
                # check if the old password is correct
                cursor = get_cursor()
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user_info = cursor.fetchone()
                if not check_password_hash(user_info[3], current_password):
                    flash('Invalid password', 'error')
                    return redirect(url_for('manage_account.change_password'))
                else:
                    if not check_password(new_password):
                        return redirect(url_for('manage_account.change_password'))
                    else:
                        # hash the new password
                        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
                        # update the password in the database
                        try:
                            cursor.execute(
                                "UPDATE users SET hashed_password = %s WHERE id = %s", (hashed_password, user_id))
                            # flash a message to the user
                            flash('Password changed successfully', 'success')
                            # clean session
                            session.pop('logged_in', False)
                            session.pop('user_id', None)
                            session.pop('role_id', None)
                            session.pop('discount_rate', None)
                            # redirect the user to the login page
                            return redirect(url_for('users.login'))  
                        except Exception as e:
                            print('An error occurred: ' + str(e))
                            # flash a message to the user
                            flash('An error occurred. Please try again later.', 'danger')
                            return redirect(url_for('manage_account.change_password'))
    return render_template('/manage_account/change_password.html')   