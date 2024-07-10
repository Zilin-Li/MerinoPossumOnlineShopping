from flask import Blueprint, request, render_template, flash, redirect, url_for
from ..controllers.corporate_client_credit_controller import get_credit_info, apply_credit_limit_increase, get_credit_info_from_db
from ..controllers.user_controllers import login_required

corporate_client_credit = Blueprint(
    'corporate_client_credit',
    __name__,
    static_folder='static',
    template_folder='templates/corporate_client_credit'
)

# Route to display credit information for corporate client
@corporate_client_credit.route('/credit_info/<int:user_id>', methods=['GET'])
@login_required
def credit_info(user_id):
    credit_info = get_credit_info(user_id)
    return render_template('corporate_client_credit/credit_info.html', credit_info=credit_info, user_id=user_id)

@corporate_client_credit.route('/apply_credit_limit_increase', methods=['POST'])
@login_required
def credit_limit_increase():
    # Get the form data from the request
    data = request.form
    user_id = int(data['user_id'])
    requested_limit = float(data['requested_limit'])
    
    credit_info = get_credit_info_from_db(user_id)
    
    # Check if the requested limit is greater than the current credit limit
    if credit_info and requested_limit > credit_info[0]:
        apply_credit_limit_increase({'user_id': user_id, 'requested_limit': requested_limit})
        flash('Credit limit increase application submitted successfully.', 'success')
    else:
        flash('Requested limit must be greater than current credit limit.', 'danger')
    
    credit_info = get_credit_info_from_db(user_id)
    return render_template('corporate_client_credit/credit_limit_increase_form.html', user_id=user_id, credit_info=credit_info)

@corporate_client_credit.route('/apply_credit_limit_increase_form/<int:user_id>', methods=['GET'])
@login_required
def credit_limit_increase_form(user_id):
    credit_info = get_credit_info_from_db(user_id)
    if credit_info:
        return render_template('corporate_client_credit/credit_limit_increase_form.html', user_id=user_id, credit_info=credit_info)
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('corporate_client_credit.credit_info', user_id=user_id))








