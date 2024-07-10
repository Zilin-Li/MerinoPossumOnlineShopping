from config import get_cursor
from flask import flash


def get_main_product_image(product_id):
    cursor = get_cursor()
    sql = """SELECT image_url FROM product_images WHERE product_id = %s AND image_type_id = 1 LIMIT 1"""
    cursor.execute(sql, (product_id,))
    main_image = cursor.fetchone()
    return main_image[0]

def get_product_color_images(product_id):
    cursor = get_cursor()
    sql = """
    SELECT DISTINCT p.image_url, p.color_id,c.color_name
    FROM product_images p
    JOIN product_colors c ON p.color_id = c.id
    WHERE product_id = %s AND (image_type_id =3 or image_type_id =1)
    """
    cursor.execute(sql, (product_id,))
    color_images = cursor.fetchall()
    return color_images

def get_product_size(product_id):
    cursor = get_cursor()
    sql = """
    SELECT DISTINCT s.size_name, p.size_id
    FROM product_variants p
    JOIN sizes s ON p.size_id = s.id
    WHERE p.product_id = %s
    order by size_id;
    """
    cursor.execute(sql, (product_id,))
    sizes = cursor.fetchall()
    return sizes

def get_product_color(product_id):
    cursor = get_cursor()
    sql = """
    SELECT DISTINCT p.color_id, c.color_name
    FROM product_variants p
    JOIN product_colors c ON p.color_id = c.id
    WHERE p.product_id = %s
    order by color_id;
    """
    cursor.execute(sql, (product_id,))
    colors = cursor.fetchall()
    return colors

def get_product_detail_by_id(product_id):
    cursor = get_cursor()
    sql = """SELECT p.id, 
        p.product_name,
        c.category_name,
        b.brand_name, 
        p.description,
        p.base_price 
        FROM products p
        JOIN brands b ON p.brand_id = b.id
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s""" 
    cursor.execute(sql, (product_id,))
    product_info = cursor.fetchone()
    return product_info


#  -------------------  cart functions -------------------
# get the product variant details
def get_product_variant(product_id, color, size):
    cursor = get_cursor()
    cursor.execute("SELECT id, stock_quantity FROM product_variants WHERE product_id = %s AND color_id = %s AND size_id = %s", (product_id, color, size))
    row = cursor.fetchone()
    return {'id': row[0], 'stock_quantity': row[1]} if row else None
    
# get the cart id of the user, if the user does not have a cart, create a new cart
def get_or_create_cart(user_id):
    

    cursor = get_cursor()
    cursor.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
    cart = cursor.fetchone()

    if not cart:
        cursor.execute("INSERT INTO carts (user_id) VALUES (%s)", (user_id,))
        cursor.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
        cart = cursor.fetchone()
    return cart[0]
    
# add the item to the cart
def process_cart_item(cart_id, product_id, product_variant, quantity, price):
    cursor = get_cursor()
    variant_id = product_variant['id']
    stock_quantity = product_variant['stock_quantity']
    cursor.execute("SELECT id, quantity FROM cart_items WHERE cart_id = %s AND variant_id = %s", (cart_id, variant_id))
    cart_item = cursor.fetchone()

    if cart_item:
        new_quantity = min(stock_quantity, cart_item[1] + quantity)
        cursor.execute("UPDATE cart_items SET quantity = %s, price = %s WHERE id = %s", (new_quantity, price, cart_item[0]))
    else:
        new_quantity = min(stock_quantity, quantity)
        cursor.execute("INSERT INTO cart_items (cart_id, product_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s, %s)", (cart_id, product_id, variant_id, new_quantity, price))

    if new_quantity < quantity:
        flash(f'Stock limit reached. Quantity adjusted to {new_quantity}.', 'warning')
    else:
        flash('Item added to cart', 'success')