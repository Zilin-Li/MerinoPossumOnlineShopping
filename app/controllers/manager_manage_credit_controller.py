from ..models.manager_manage_credit_model import get_credit_info_from_db, insert_credit_limit_increase_request, update_credit_limit, fetch_all_clients, fetch_credit_limit_increase_requests, approve_credit_limit_request

def get_credit_info(user_id):
    return get_credit_info_from_db(user_id)

def apply_credit_limit_increase(data):
    insert_credit_limit_increase_request(data['user_id'], data['requested_limit'])

def adjust_credit_limit(user_id, new_limit, manager_id):
    credit_info = get_credit_info_from_db(user_id)
    if credit_info:
        old_limit = credit_info['credit_limit']
        update_credit_limit(user_id, new_limit)

def monitor_credit_utilization():
    return fetch_all_clients()

def get_credit_limit_increase_requests(user_id):
    return fetch_credit_limit_increase_requests(user_id)

def approve_credit_limit_increase(request_id):
    approve_credit_limit_request(request_id)











    

