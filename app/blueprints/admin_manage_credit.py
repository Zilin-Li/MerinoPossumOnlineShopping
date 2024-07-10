from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from ..controllers.admin_manage_credit_controller import get_credit_info, apply_credit_limit_increase, adjust_credit_limit, monitor_credit_utilization, get_credit_limit_increase_requests, approve_credit_limit_increase
from config import get_cursor

admin_manage_credit = Blueprint(
    'admin_manage_credit',
    __name__,
    static_folder='static',
    template_folder='templates/admin_manage_credit'
)

# Add context processor to inject current_user into templates
@admin_manage_credit.context_processor
def inject_user():
    user_id = session.get('user_id')
    user = get_user_from_db(user_id) if user_id else None
    return dict(current_user=user)

# Function to retrieve user information from the database
def get_user_from_db(user_id):
    cursor = get_cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return {
            'id': user[0],
            'username': user[1]
        }
    return None
# Route to display credit information for a specific user
@admin_manage_credit.route('/credit_info/<int:user_id>', methods=['GET'])
def credit_info(user_id):
    credit_info = get_credit_info(user_id)
    if credit_info:
        return render_template('admin_manage_credit/admin_edit_credit.html', credit_info=credit_info, user_id=user_id)
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('admin_manage_credit.monitor_credit_utilization_route'))
# Route to handle the submission of a credit limit increase request
@admin_manage_credit.route('/apply_credit_limit_increase', methods=['POST'])
def credit_limit_increase():
    data = request.form
    user_id = int(data['user_id'])
    requested_limit = float(data['requested_limit'])

    credit_info = get_credit_info(user_id)
    if credit_info and requested_limit > credit_info['credit_limit']:
        apply_credit_limit_increase({'user_id': user_id, 'requested_limit': requested_limit})
        flash('Credit limit increase application submitted successfully.', 'success')
    else:
        flash('Requested limit must be greater than current credit limit.', 'danger')

    return redirect(url_for('admin_manage_credit.credit_info', user_id=user_id))
# Route to display the form for requesting a credit limit increase
@admin_manage_credit.route('/apply_credit_limit_increase_form/<int:user_id>', methods=['GET'])
def credit_limit_increase_form(user_id):
    credit_info = get_credit_info(user_id)
    if credit_info:
        return render_template('admin_manage_credit/credit_limit_increase_form.html', user_id=user_id, credit_info=credit_info)
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('admin_manage_credit.monitor_credit_utilization_route'))
# Route to handle adjusting the credit limit for a corporate client
@admin_manage_credit.route('/adjust_credit_limit', methods=['POST'])
def adjust_credit_limit_route():
    data = request.form
    user_id = int(data['user_id'])
    new_limit = float(data['new_limit'])
    admin_id = session.get('user_id')

    credit_info = get_credit_info(user_id)
    if credit_info:
        adjust_credit_limit(user_id, new_limit, admin_id)
        flash('Credit limit adjusted successfully.', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('admin_manage_credit.credit_info', user_id=user_id))
# Route to monitor credit utilization for all clients
@admin_manage_credit.route('/monitor_credit_utilization', methods=['GET'])
def monitor_credit_utilization_route():
    clients = monitor_credit_utilization()
    return render_template('admin_manage_credit/admin_manage_credit.html', clients=clients)
# Route to view credit limit increase requests for a specific user
@admin_manage_credit.route('/credit_limit_requests/<int:user_id>', methods=['GET'])
def credit_limit_requests(user_id):
    requests = get_credit_limit_increase_requests(user_id)
    return render_template('admin_manage_credit/admin_check_request.html', requests=requests, user_id=user_id)
# Route to approve a credit limit increase request
@admin_manage_credit.route('/approve_credit_limit/<int:request_id>', methods=['POST'])
def approve_credit_limit(request_id):
    approve_credit_limit_increase(request_id)
    flash('Credit limit increase approved.', 'success')
    return redirect(url_for('admin_manage_credit.monitor_credit_utilization_route'))













