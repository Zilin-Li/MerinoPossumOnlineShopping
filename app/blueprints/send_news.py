from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from config import get_cursor
from ..controllers.user_controllers import get_session_info

# SCRUM-31 manager or administrator send news by Danfeng
send_news = Blueprint(
    'send_news',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# manager or administrator add a news
@send_news.route('/add_news', methods=['GET','POST'])
def add_news():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        if request.method == 'POST':            
            news =request.form.get('news')
            try:    
                cursor = get_cursor()               
                cursor.execute('INSERT INTO news (news_content) VALUES (%s)', (news,))
                flash('Add the news successfully', 'success')
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')
    
        news_list = []
        try:
            cursor = get_cursor()
            cursor.execute("SELECT * FROM news")
            news_list = cursor.fetchall()  
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
  
        return render_template('/send_news/show_news.html', news_list = news_list)  
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 
    
# manager or administrator select a news
@send_news.route('/select_news', methods=['GET','POST'])
def select_news():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        if request.method == 'POST':
            selected_news_id = request.form.get('selected_news_id')
            try:    
                cursor = get_cursor()            
                cursor.execute('UPDATE news SET selected = 1 WHERE id= %s', (selected_news_id,))
                cursor.execute('UPDATE news SET selected = 0 WHERE id!= %s', (selected_news_id,))
                flash('Select the news successfully', 'success')
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')
           
        news_list = []      
        try:
            cursor = get_cursor()
            cursor.execute("SELECT * FROM news")
            news_list = cursor.fetchall()  
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
  
        return render_template('/send_news/show_news.html', news_list = news_list)  
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 
    
# manager or administrator edit a news
@send_news.route('/edit_news/<int:news_id>', methods=['GET','POST'])
def edit_news(news_id):
    is_login, user_id, role_id, discount_rate = get_session_info()
    if is_login ==True and (session.get('is_manager')==1 or session.get('is_admin')==1):
        if request.method == 'POST':
            news = request.form.get('news')
            try:    
                cursor = get_cursor()            
                cursor.execute('UPDATE news SET news_content = %s WHERE id= %s', (news, news_id))   
                flash('Edit the news successfully', 'success')
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')
           
        news_detail = []      
        try:
            cursor = get_cursor()
            cursor.execute("SELECT * FROM news WHERE id = %s",(news_id, ))
            news_detail = cursor.fetchone()  
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
  
        return render_template('/send_news/edit_news.html', news_detail = news_detail)  
    else:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login')) 