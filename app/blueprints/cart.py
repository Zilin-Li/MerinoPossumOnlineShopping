import re
from config import get_cursor
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..controllers.user_controllers import login_required, get_session_info
# from ..controllers.product_controller import get_or_create_cart
# from ..controllers.cart_controller import update_cart_item_quantities,get_cart_items_by_cartid, get_product_detai_by_cart_item_id, get_cart_items_image
from decimal import Decimal


cart = Blueprint(
    'cart',
    __name__,
    static_folder='static',
    template_folder='templates'
)

@cart.route('/')
@login_required
def display_cart():
     # get user_id and role_id from session
    is_login, user_id, role_id,discount_rate = get_session_info()
    # check if user has a cart
    dbconn = get_cursor()
    dbconn.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
    cart = dbconn.fetchone()
    # if user does not have a cart, flash a message to the user that the cart is empty  
    if not cart:
        return render_template('cart/shopping_cart_page.html')
    # if user has a cart, get the items in the cart
    else:
        dbconn.execute("SELECT * FROM cart_items WHERE cart_id=%s", (cart[0],))
        cart_items = dbconn.fetchall()
        # if cart_items is empty, flash a message to the user that the cart is empty
        if not cart_items:
            return render_template('cart/shopping_cart_page.html')
        # if cart_items is not empty, get the details of the items in the cart
        else:
            cart_items_list = []
            cart_total = 0
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
                    p.base_price,
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
                    cart_total += total_price_for_item
                    cart_total =Decimal(cart_total)
                    percent_to_earn = Decimal("0.10")  
                    order_points = cart_total * percent_to_earn

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
            
            return render_template('cart/shopping_cart_page.html',cart_items_list=cart_items_list, cart_total=cart_total,order_points=order_points)

@cart.route('/update_cart_item', methods=['POST'])
@login_required
def update_cart_item():
    #get updated quantity and cart_item_id from the form
    cart_updates = {}
    for key in request.form:
        if key.startswith('quantity_'):
            cart_item_id = key.split('_')[1]   
            quantity = request.form[key]            
            try:
                quantity = int(quantity)
                cart_updates[cart_item_id] = quantity
            except ValueError:                
                print(f"Invalid quantity for cart item {cart_item_id}")
    update_cart_item_quantities(cart_updates)
    flash("Cart updated successfully!", "success")
    return redirect(url_for('cart.display_cart'))

def update_cart_item_quantities(cart_updates):
    dbconn = get_cursor()  
    try:
        for cart_item_id, quantity in cart_updates.items():
            if quantity > 0:
                update_query = "UPDATE cart_items SET quantity=%s WHERE id=%s"
                dbconn.execute(update_query, (quantity, cart_item_id))
            else:
                print(f"Invalid quantity {quantity} for cart item {cart_item_id}")
    except Exception as e:
        print("An error occurred:", e)
        dbconn.rollback() 
        
@cart.route('/delete_cart_item/<int:cart_item_id>', methods=['GET'])
@login_required
def delete_cart_item(cart_item_id):
    dbconn = get_cursor()
    dbconn.execute("DELETE FROM cart_items WHERE id=%s", (cart_item_id,))
    return redirect(url_for('cart.display_cart'))
