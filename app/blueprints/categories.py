import re
from config import get_cursor
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..controllers.product_controller import get_products_by_category, get_product_complete_detail,get_product_variant, get_or_create_cart, process_cart_item,generate_card_number,format_product_details,format_product_details_for_customer,get_product_complete_detail_for_customer
from ..controllers.user_controllers import login_required, get_session_info
from datetime import datetime
from random import SystemRandom

categories = Blueprint(
    'categories',
    __name__,
    static_folder='static',
    template_folder='templates'
)

@categories.route('/<category_name>/<int:category_id>', methods=['GET'])
def display_products(category_name, category_id):
    dbconn = get_cursor()
    is_login, user_id, role_id,discount_rate = get_session_info()
    sort_by = request.args.get('sort_by', 'price_low_to_high')
    dbconn.execute("SELECT parent_category_id, description FROM categories WHERE id = %s", (category_id,))
    category_info = dbconn.fetchone()
    parent_category_id = category_info[0]
    new_category_name = category_info[1] 

    if not parent_category_id:
        dbconn.execute("SELECT id FROM categories WHERE parent_category_id = %s", (category_id,))
        sub_categories = dbconn.fetchall()
        # base price
        products = get_products_by_category(category_id)
        if sub_categories:   
            for sub_category in sub_categories:
                products += get_products_by_category(sub_category[0])    
    else:
        products = get_products_by_category(category_id) 

    # if client, get discount rate from session  
    if role_id == 2:
        discount_rate = float(session.get('discount_rate', 1))
        # if client, change price to discount price
        # Convert products to dictionaries and calculate discounted prices
        products_dicts = format_product_details(products, discount_rate)
    else:
        # if client, change price to discount price
        # Convert products to dictionaries and calculate discounted prices
        products_dicts = format_product_details_for_customer(products)
        

    # Apply sorting
    if sort_by == 'price_low_to_high':
        products_dicts.sort(key=lambda x: x['discounted_price'])
    elif sort_by == 'price_high_to_low':
        products_dicts.sort(key=lambda x: x['discounted_price'], reverse=True)
    elif sort_by == 'availability':
        products_dicts = [product for product in products_dicts if product['total_stock_quantity'] > 0]

    return render_template('products/product_display.html', products=products_dicts, new_category_name=new_category_name, category_id=category_id, sort_by=sort_by)


@categories.route('/<int:product_id>', methods=['GET'])
def display_product_detail(product_id):
    is_login, user_id, role_id,discount_rate = get_session_info()

    # Fetch discount rate from session; default to 1 (no discount)
    if role_id == 2:
        discount_rate = float(session.get('discount_rate', 1))
        # if client, change price to discount price
        product_detail = get_product_complete_detail(product_id, discount_rate)
    else:
        # if client, change price to discount price
        product_detail = get_product_complete_detail_for_customer(product_id)
    return render_template('products/product_detail.html',product_detail=product_detail)



@categories.route('/add_item', methods=['POST'])
@login_required
def add_item_to_cart():
    
    is_login, user_id, role_id,discount_rate = get_session_info()
   
  
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 0))
    color = request.form.get('select_color',None)
    size = request.form.get('select_size',None)
    price = float(request.form.get('product_price', 0))

    # if is_login == False:
    #     flash('Please login to add items to cart.', 'error')
    #     return redirect(url_for('categories.display_product_detail', product_id=product_id))
    if role_id ==3:
        flash('Only customers can add items to cart.', 'error')
        return redirect(url_for('categories.display_product_detail', product_id=product_id))

    if not (color and size):
        flash('Please select a color and size.', 'error')
        return redirect(url_for('categories.display_product_detail', product_id=product_id))

    dbconn = get_cursor()
    product_variant = get_product_variant(product_id, color, size)
    if not product_variant or product_variant['stock_quantity'] == 0:
        flash('Out of stock', 'error')
        return redirect(url_for('categories.display_product_detail', product_id=product_id))
    
    cart_id = get_or_create_cart( user_id)
    process_cart_item(cart_id, product_id, product_variant, quantity, price)

    return redirect(url_for('categories.display_product_detail', product_id=product_id))

@categories.route('/gift_cards')
def gift_cards():
    #get all gift cards from the database
    dbconn = get_cursor()
    dbconn.execute("SELECT * FROM gift_cards_types where is_active=1;")
    gift_cards = dbconn.fetchall()
    gift_card_list = []
    each_gift_card = {}
    for gift_card in gift_cards:
        each_gift_card = {
            'id': gift_card[0],
            'type_name': gift_card[1],
            'value': gift_card[2],
            'description': gift_card[3]
        }
        gift_card_list.append(each_gift_card)

    return render_template('products/gift_cards.html', gift_card_list=gift_card_list)

@categories.route('/purchase_cards', methods=['post'])
@login_required
def purchase_gift_card():
    is_login, user_id, role_id,discount_rate = get_session_info()
    if role_id != 1:
        flash('Only customers can purchase gift cards.', 'error')
        return redirect(url_for('categories.gift_cards'))
         #get the gift card amount and type
    gift_card_type_id = request.form.get('amount')
    gift_card_quantity = request.form.get('quantity')

    # if gift_card_amount is none, return error message
    if not gift_card_type_id:
        flash('Please select a gift card amount.', 'error')
        return redirect(url_for('categories.gift_cards'))

    card_value = 0
    #get the gift card value
    dbconn = get_cursor()
    dbconn.execute("SELECT value FROM gift_cards_types WHERE id = %s", (gift_card_type_id,))
    card_value = dbconn.fetchone()[0]

    # based on the quantity of gift card, generate gift card code and store in the database
    for i in range(int(gift_card_quantity)):
        # generate a unique gift card code
        card_number = "BSMP"+generate_card_number(16)+"AK"
        message_content = "You have successfully purchased a gift card with the value of $"+str(card_value)+". Your gift card code is: "+card_number
        # store the gift card code in the database
        purchase_time = datetime.now()
        dbconn.execute("INSERT INTO gift_cards (user_id,type_id,card_number, balance, purchase_time) VALUES (%s, %s,%s,%s, %s)", (user_id,gift_card_type_id, card_number, card_value,purchase_time))

        #send message to the user
        dbconn.execute("INSERT INTO messages (send_id, receive_id, message_content,created_at,message_type_id) VALUES (%s, %s,%s, %s, %s)", (4, user_id, message_content, datetime.now(),1))

    flash('Gift card purchased successfully.', 'success')
    return redirect(url_for('categories.gift_cards'))

    

