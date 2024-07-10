from config import get_cursor

def get_cart_items_by_cartid(cart_id):
    dbconn = get_cursor()
    dbconn.execute("SELECT * FROM cart_items WHERE cart_id=%s", (cart_id,))
    cart_items = dbconn.fetchall()
    return cart_items 

def get_product_detai_by_cart_item_id(cart_item_id):
    dbconn = get_cursor()
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
    dbconn.execute(select_query, (cart_item_id,))
    product_detail = dbconn.fetchone()
    return product_detail if product_detail else None

def get_cart_items_image(product_id,color_id):
    dbconn = get_cursor()
    select_query="""
    SELECT
        pi.image_url
    FROM product_images pi
    WHERE pi.product_id = %s AND pi.color_id = %s;
    """
    dbconn.execute(select_query, (product_id,color_id))
    product_images = dbconn.fetchall()
    return product_images if product_images else None

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