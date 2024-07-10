from config import get_cursor
from flask import flash

# get all the orders of a customer by Danfeng
def get_orders(user_id):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id=%s ORDER BY order_date DESC", (user_id,))
    orders = cursor.fetchall()
    return orders

# get the product details of an order by Danfeng
def get_order_info(order_id):
    cursor = get_cursor()
    order_detail = []
    try:
        sql="""
            SELECT DISTINCT od.product_id, p.product_name, (SELECT image_url FROM product_images WHERE product_id= od.product_id AND color_id=pv.color_id ORDER BY id ASC LIMIT 1) AS image, pc.color_name, s.size_name, od.price, od.quantity, od.price*od.quantity 
            FROM order_details od
            JOIN products p ON od.product_id=p.id
            JOIN product_variants pv  ON od.variant_id=pv.id
            JOIN product_colors pc ON pv.color_id=pc.id
            JOIN sizes s ON pv.size_id=s.id
            JOIN product_images pi ON p.id=pi.product_id
            WHERE od.order_id=%s;
        """
        cursor.execute(sql, (order_id,))
        order_detail = cursor.fetchall()  
        return  order_detail                 
    except Exception as e:
        print(f"An error occurred: {e}")  
        flash('An error occurred. Please try again later.', 'danger') 
        return order_detail             

# get the product details of an order by Danfeng
def get_order_info(order_id):
    cursor = get_cursor()
    order_detail = []
    try:
        sql="""
            SELECT DISTINCT od.product_id, p.product_name, (SELECT image_url FROM product_images WHERE product_id= od.product_id AND color_id=pv.color_id ORDER BY id ASC LIMIT 1) AS image, pc.color_name, s.size_name, od.price, od.quantity, od.price*od.quantity 
            FROM order_details od
            JOIN products p ON od.product_id=p.id
            JOIN product_variants pv  ON od.variant_id=pv.id
            JOIN product_colors pc ON pv.color_id=pc.id
            JOIN sizes s ON pv.size_id=s.id
            JOIN product_images pi ON p.id=pi.product_id
            WHERE od.order_id=%s;
        """
        cursor.execute(sql, (order_id,))
        order_detail = cursor.fetchall()  
        return  order_detail                 
    except Exception as e:
        print(f"An error occurred: {e}")  
        flash('An error occurred. Please try again later.', 'danger') 
        return order_detail             

# get the summary info of an order by Danfeng
def get_order_sum(order_id):
    cursor = get_cursor()
    order_sum = []
    try:
        sql="""
            SELECT total_incl_gst, invoices.shipping_fee, total_amount, delivery_street, delivery_city, delivery_state, delivery_country, delivery_post_code, order_note, orders.user_id 
            FROM orders 
            JOIN invoices on orders.id=invoices.order_id 
            WHERE orders.id=%s;
        """
        cursor.execute(sql, (order_id,))
        order_sum = cursor.fetchone()  
        return  order_sum                 
    except Exception as e:
        print(f"An error occurred: {e}")  
        flash('An error occurred. Please try again later.', 'danger') 
        return order_sum             

