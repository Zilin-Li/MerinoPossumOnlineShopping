import re
from config import get_cursor
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..controllers.user_controllers import login_required, get_session_info
from decimal import Decimal, ROUND_HALF_UP
from flask import jsonify
# import pymysql

checkout = Blueprint(
    'checkout',
    __name__,
    static_folder='static',
    template_folder='templates'
)

@checkout.route('/')
@login_required
def display_checkout_page():
    redirect_url = 'checkout/checkout_page.html'
    is_login, user_id, role_id,discount_rate = get_session_info()
    
    
    dbconn = get_cursor()
    dbconn.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
    cart = dbconn.fetchone()
    # if user does not have a cart, flash a message to the user that the cart is empty  
    if not cart:
        return render_template(redirect_url)
    # if user has a cart, get the items in the cart
    else:
        dbconn.execute("SELECT * FROM cart_items WHERE cart_id=%s", (cart[0],))
        cart_items = dbconn.fetchall()
        # if cart_items is empty, flash a message to the user that the cart is empty
        if not cart_items:
            return render_template(redirect_url)
        # if cart_items is not empty, get the details of the items in the cart
        else:
            cart_items_list = []
            cart_subtotal = Decimal('0.00')
            shipping_fee =Decimal('10.00')
            
            for cart_item in cart_items:
                # create a dictionary to store the details of the cart item
                cart_item_details = {}
                # get the details of the cart item from the cart_items table
                cart_item_details['cart_item_id'] = cart_item[0]
                cart_item_details['product_id'] = cart_item[2]
                cart_item_details['variant_id'] = cart_item[3]
                cart_item_details['order_quantity'] = cart_item[4]
                cart_item_details['order_price'] = cart_item[5]
                # get more details of the cart item from the product_variants, products, product_colors, sizes, and product_images tables
                select_query="""
                SELECT
                    p.product_name,
                    p.is_active,
                    pc.color_name,
                    s.size_name,
                    pv.stock_quantity,
                    p.base_price + pv.additonal_price,
                    pv.color_id
                FROM product_variants pv
                    JOIN products p ON pv.product_id = p.id
                    JOIN product_colors pc ON pv.color_id = pc.id
                    JOIN sizes s ON pv.size_id = s.id
                WHERE pv.id = %s;
                """
                dbconn.execute(select_query, (cart_item[3],))
                product_detail = dbconn.fetchone()
                if not product_detail:
                    flash('Product not found', 'error')
                    # return render_template('cart/shopping_cart_page.html')
                else:
                    total_price_for_item = cart_item[4] * cart_item[5]  # order_quantity * current_price
                    cart_subtotal += total_price_for_item
                    cart_subtotal = Decimal(cart_subtotal).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                    percent_to_earn = Decimal("0.10")  
                    order_points = (cart_subtotal * percent_to_earn).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

                    # add the product details to the cart_item_details dictionary
                    cart_item_details['product_name'] = product_detail[0]
                    cart_item_details['is_active'] = product_detail[1]
                    cart_item_details['color_name'] = product_detail[2]
                    cart_item_details['size_name'] = product_detail[3]
                    cart_item_details['stock_quantity'] = product_detail[4]
                    cart_item_details['current_price'] = product_detail[5]
                    cart_item_details['price_changed'] = cart_item[5] != product_detail[5]
                    cart_item_details['out_of_stock'] = cart_item[4] > product_detail[4]

                    # get product image urls
                    select_query="""
                    SELECT
                        pi.image_url
                    FROM product_images pi
                    WHERE pi.product_id = %s AND pi.color_id = %s;
                    """
                    dbconn.execute(select_query, (cart_item[2],product_detail[6]))
                    product_images = dbconn.fetchall()

                    # add the product image urls to the cart_item_details dictionary
                    cart_item_details['image_urls'] = [product_image[0] for product_image in product_images]
                    #calculate the total price of the cart
                   
                # add the cart_item_details to the cart_items_list
                cart_items_list.append(cart_item_details)
            gst = (cart_subtotal * Decimal(0.15)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            if cart_subtotal >= Decimal('200.00'):
                shipping_fee = Decimal('0.00')
             # calculate the total price of the cart   
            cart_total_calculate = {
                'cart_subtotal': cart_subtotal,
                'order_points': order_points,
                'gst': gst,
                'shipping_fee': shipping_fee,  
                'total_incl_gst_and_shipping': (cart_subtotal + gst + shipping_fee).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            }
            return render_template(redirect_url, cart_items_list=cart_items_list, cart_total_calculate=cart_total_calculate)

@checkout.route('/apply_gift_card', methods=['POST'])
@login_required
def apply_gift_card():
    is_login, user_id, role_id,discount_rate = get_session_info()
    cursor = get_cursor()
    data = request.get_json()
    if data is not None:
        card_code = data.get('gift_card_code')
        if not card_code:
            flash('Gift card code is required', 'danger')
            return jsonify({'status': 'error', 'message': 'Gift card code is required'}), 400        
        cursor.execute('SELECT balance FROM gift_cards WHERE card_number = %s', (card_code,))
        card_balance = cursor.fetchone()
        if card_balance:
            card_balance = card_balance[0]
        else:
            card_balance = 0     
        return jsonify({'status': 'success', 'balance': card_balance, 'card_code': card_code})
    else:
        flash('No data received', 'danger')
        return jsonify({'status': 'error', 'message': 'No data received'}), 400

@checkout.route('/confirm_order', methods=['POST'])
@login_required
def confirm_order():
    is_login, user_id, role_id,discount_rate = get_session_info()
    cursor = get_cursor()
   
    order_info = request.form
    gift_card_code = order_info.get('card-number', None)
   
    # get delivery-option from form
    delivery_option = order_info.get('delivery_option')
    payment_option = order_info.get('paymentType')
    # if user choose payment_option and payment_option is "monthly"
    # check user's cridit limit whether enough to pay the order
    
    # if delivery option is delivery
    if delivery_option == 'delivery':
        
        first_name = order_info['first_name']
        last_name = order_info['last_name'] 
        username = first_name + ' ' + last_name
        street = order_info['street']
        city = order_info['city']
        state = order_info['state']
        country = order_info['country']
        postcode = order_info['postcode']
        phone = order_info['phone']

        if country=="nz":
            shipping_fee = Decimal('10.00')
        elif country=="aus":
            shipping_fee = Decimal('40.00')
        elif country=="usa" or country=="can":
            shipping_fee = Decimal('60.00')
        elif country =="uk" or country=="eur":
            shipping_fee = Decimal('70.00')     
    else:
        # get username from database by user_id      
        cursor.execute('SELECT first_name, last_name,phone FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        if user:
            first_name = user[0]
            last_name = user[1]
            username = first_name + ' ' + last_name
        else:
            flash('User not found', 'danger')
            return redirect(url_for('checkout.display_checkout_page'))
        street = 'pickup'
        city = 'pickup'
        state = 'pickup'
        country = 'pickup'
        postcode = 'pickup'
        # if phone number is none, set phone number to 0
        phone = user[2] if user[2] else 'pickup'
        shipping_fee = Decimal('0.00')
    # get cart id from user id
    cursor.execute('SELECT id FROM carts WHERE user_id = %s', (user_id,))
    cart = cursor.fetchone()
    if cart: 
        cart_id = cart[0]
    else:
        flash('Cart not found', 'danger')
        return redirect(url_for('checkout.display_checkout_page'))

    # get cart items from cart id
    cursor.execute('SELECT * FROM cart_items WHERE cart_id = %s', (cart_id,))
    cart_items = cursor.fetchall()
   
    if not cart_items:
        flash('Cart is empty', 'danger')
        return redirect(url_for('checkout.display_checkout_page'))
    else:
        # calculate order total
        total_excl_gst = Decimal('0.00')
        
        is_paid= True
        for item in cart_items:
            total_excl_gst +=  item[4] * item[5]
        total_excl_gst = Decimal(total_excl_gst).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        if total_excl_gst >= Decimal('200.00') and (delivery_option == 'delivery' and country=="nz"):
            shipping_fee = Decimal('0.00')            
        gst = total_excl_gst * Decimal(0.15)
        total_incl_gst = total_excl_gst + gst
        total_amount= total_incl_gst + shipping_fee
        status_id = 1
        order_note=''
        total_points = 0
        card_balance_change = Decimal('0.00')
        payment_type_id = 1

        # Format cart items data to json
        cart_items =[
            {
                'product_id': item[2],
                'variant_id': item[3], # 'variant_id': 'null
                'quantity': item[4],
                'price': item[5],
                'points': 0
            }
            for item in cart_items
        ]
        # check if user choose payment option and payment option is "monthly"
        if role_id==2 and payment_option == 'monthly':
            is_paid = False
            cursor.execute('SELECT available_credit FROM corporate_clients WHERE user_id = %s', (user_id,))
            available_credit = cursor.fetchone()
            if available_credit:
                available_credit = Decimal(available_credit[0])
            else:
                available_credit = Decimal('0.00')
            if available_credit < total_amount:
                flash('Credit limit is not enough.Please choose another payment method.', 'danger')
                return redirect(url_for('checkout.display_checkout_page'))
            else:
                new_available_credit = available_credit - Decimal(total_amount)
                new_available_credit = new_available_credit.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                # total_amount = Decimal('0.00')
    
        # check if user use a gift card,Only customer can use gift card
        if role_id==1 and gift_card_code:
            cursor.execute('SELECT balance FROM gift_cards WHERE card_number = %s', (gift_card_code,))
            card_balance = cursor.fetchone()
            if card_balance:
                card_balance = Decimal(card_balance[0])
            else:
                card_balance = Decimal('0.00')

            if card_balance >= total_amount:
                new_total_amount =  Decimal('0.00')
                new_card_balance = card_balance - total_amount
                card_balance_change = -total_amount
                payment_type_id = 2

                # cursor.execute('UPDATE gift_cards SET balance = %s WHERE card_number = %s', (new_card_balance, gift_card_code))
            else:
                new_total_amount = total_amount - card_balance
                new_card_balance =  Decimal('0.00')
                card_balance_change = -card_balance
                # cursor.execute('UPDATE gift_cards SET balance = %s WHERE card_number = %s', (new_card_balance, gift_card_code))

            # check if user use a gift card
        new_total_amount = new_total_amount if gift_card_code else total_amount

        # try:
        # insert order into order table
        sql_query = """INSERT INTO orders (user_id, order_date, total_excl_gst,total_points,status_id, recipient_name, recipient_mobile, delivery_street, delivery_city, delivery_state, delivery_country, delivery_post_code, order_note) VALUES (%s, NOW(),%s, %s,  %s,%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_query, (user_id, total_excl_gst, total_points,status_id, username, phone, street, city, state, country, postcode, order_note))
        
        order_id = cursor.lastrowid
        # insert order items into order_item table
        for item in cart_items:
            cursor.execute('INSERT INTO order_details (order_id, product_id,variant_id, quantity, price, points) VALUES (%s, %s, %s, %s,%s,%s)', (order_id, item['product_id'], item['variant_id'], item['quantity'], item['price'],item['points']))
            # update product quantity
            cursor.execute('UPDATE product_variants SET stock_quantity = stock_quantity - %s WHERE id = %s', (item['quantity'], item['variant_id']))
        
        #create invoices data  
        cursor.execute('INSERT INTO invoices (user_id,order_id, total_incl_gst, shipping_fee, total_amount, is_paid) VALUES (%s, %s, %s, %s, %s, %s)', (user_id, order_id, total_incl_gst, shipping_fee, total_amount, is_paid))
        invoice_id = cursor.lastrowid
        # delete cart items from cart_item table
        cursor.execute('DELETE FROM cart_items WHERE cart_id = %s', (cart_id,))
        
        # if user use a gift card, update gift card balance
        if role_id==1 and gift_card_code:
            cursor.execute('UPDATE gift_cards SET balance = %s WHERE card_number = %s', (new_card_balance, gift_card_code))
            # update gift card transaction
            cursor.execute('INSERT INTO gift_card_transactions (card_id, order_id, balance_change, transaction_date) VALUES((SELECT id FROM gift_cards WHERE card_number = %s), %s, %s, NOW())', (gift_card_code, order_id, card_balance_change))
        
        # if user is a corporate client, update available credit
        if role_id==2 and payment_option == 'monthly':
            cursor.execute('UPDATE corporate_clients SET available_credit = %s WHERE user_id = %s', (new_available_credit, user_id))

        if role_id==2 and payment_option != 'monthly':   
            cursor.execute('INSERT INTO payments (user_id, invoice_id, payment_date, payment_type_id) VALUES (%s, %s, NOW(), %s)', (user_id,order_id, payment_type_id) ) 

        # if user is a customer, update points, and point transaction,generate payment data
        if role_id == 1:
            # get total points earned
            earn_points = int(round(new_total_amount * Decimal('0.10')))
            # update customer points
            cursor.execute('UPDATE customers SET point = point + %s WHERE user_id = %s', (earn_points, user_id))          
            # update point transaction
            cursor.execute('INSERT INTO reward_transactions (point_change, transaction_date, user_id, order_id) VALUES (%s, NOW(), %s, %s)', (earn_points, user_id, order_id))  
            # generate payment data
            cursor.execute('INSERT INTO payments (user_id, invoice_id, payment_date, payment_type_id) VALUES (%s, %s, NOW(), %s)', (user_id,order_id, payment_type_id) ) 


        # redirect to order list page
        flash('Order has been placed', 'success')
        return redirect(url_for('cart.display_cart'))

        # except Exception as e:
        #     flash('Failed to create invoice', 'danger')
        #     return redirect(url_for('checkout.display_checkout_page'))

       

