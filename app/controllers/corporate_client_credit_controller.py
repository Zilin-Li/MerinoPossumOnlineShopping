from ..models.corporate_client_credit_model import get_credit_info_from_db, insert_credit_limit_increase_request

def get_credit_info(user_id):
    credit_info = get_credit_info_from_db(user_id)
    if credit_info:
        return {
            "credit_limit": credit_info[0],
            "available_credit": credit_info[1]
        }
    else:
        return None

def apply_credit_limit_increase(data):
    user_id = data['user_id']
    requested_limit = data['requested_limit']
    insert_credit_limit_increase_request(user_id, requested_limit)
    return "Credit limit increase application submitted"



    

