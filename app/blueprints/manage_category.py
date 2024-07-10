from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from config import get_cursor
from ..controllers.user_controllers import get_session_info

# SCRUM-41 administrator manage category by Danfeng
manage_category = Blueprint(
    'manage_category',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# manager or administrator display all categorys
@manage_category.route('/')
def display_category():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and session.get('is_admin')==1:    
        category_list = []
        try:
            cursor = get_cursor()
            cursor.execute('SELECT id, category_name FROM categories WHERE parent_category_id IS NULL')
            category_list = cursor.fetchall()  
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')  
        return render_template('/manage_category/display_category.html', category_list = category_list)  
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))     
    
# manager or administrator view and edit a specific category
@manage_category.route('/edit_category/<int:category_id>', methods=['GET','POST'])
def edit_category(category_id):
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and session.get('is_admin')==1: 
        if request.method == 'POST':
            category_id = request.form.get('category_id')
            category_name = request.form.get('category_name')
            try:    
                cursor = get_cursor() 
                update_category_query = "UPDATE categories SET category_name = %s WHERE id = %s"
                cursor.execute(update_category_query, (category_name, category_id ))
                flash('Update the category name successfully', 'success')
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')
  
        return redirect(url_for('manage_category.display_category'))  
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 
    
# manager or administrator add a new category
@manage_category.route('/add_category', methods=['GET','POST'])
def add_category():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        if request.method == 'POST':
            category_name = request.form.get('category_name')            
            description = request.form.get('description', '')
                  
            cursor = get_cursor()
            try:  
                cursor.execute(
                    "INSERT INTO categories (category_name, description) VALUES (%s, %s)",
                    (category_name, description)
                )
                flash(
                    'Your have added a new category', 'success')
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')  

        return render_template('/manage_category/add_category.html')
    
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 