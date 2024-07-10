from config import get_cursor


# get a user by Danfeng
def get_a_user(user_id):
    cursor = get_cursor()
    try:
        cursor.execute("SELECT username, email, first_name, last_name, phone, street_address, city, state, country, post_code FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return user
        else:
            print(f"No user found with ID: {user_id}")
            return None   
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  

# get an employee by Danfeng
def get_an_employee(user_id):
    cursor = get_cursor()
    try:
        cursor.execute("SELECT username, email, first_name, last_name, phone, street_address, city, state, country, post_code, hire_date, job_title FROM users JOIN employees on users.id=employees.user_id WHERE users.id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return user
        else:
            print(f"No user found with ID: {user_id}")
            return None   
    except Exception as e:
        print(f"An error occurred: {e}")
        return None 