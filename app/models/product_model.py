from config import get_cursor
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


# get all products
def get_products():
    cursor = get_cursor()
    sql = """SELECT DISTINCT
        p.id AS product_id,
        p.product_name,
        sq.total_stock_quantity,
        p.description AS product_description,
        (p.base_price + v.price_change) AS price,
        p.base_price,
        v.price_change,
        p.is_active,
        c.category_name,
        b.brand_name,
        img.image_url,
        'Main Image' AS image_type
    FROM
        products p
    LEFT JOIN 
        categories c ON p.category_id = c.id
    LEFT JOIN 
        brands b ON p.brand_id = b.id
    LEFT JOIN 
        product_variants v ON p.id = v.product_id
    LEFT JOIN (   
        SELECT
        product_id,
        SUM(stock_quantity) AS total_stock_quantity
    FROM
        product_variants
    GROUP BY
        product_id
    ) AS sq ON
        p.id = sq.product_id
    LEFT JOIN (
        SELECT
            pim.product_id,
            pim.image_url
        FROM
            product_images pim
        LEFT JOIN image_types it ON
            pim.image_type_id = it.id
        WHERE
            it.name = 'Main'
    ) AS img ON
        p.id = img.product_id
    ORDER BY p.id;
    """
    cursor.execute(sql)
    products = cursor.fetchall()
    return products


# get products by category
def get_products_by_category(category_id):
    cursor = get_cursor()
    sql = """SELECT DISTINCT
        p.id AS product_id,
        p.product_name,
       CAST(COALESCE(sq.total_stock_quantity, 0) AS SIGNED) as total_stock_quantity,
        p.description AS product_description,
        p.base_price,
        v.additonal_price,
        p.is_active,
        c.category_name,
        b.brand_name,
        COALESCE(img.image_url, 'image-not-found.jpg') AS image_url,
        'Main Image' AS image_type,
        c.description
    FROM
        products p
    LEFT JOIN 
        categories c ON p.category_id = c.id
    LEFT JOIN 
        brands b ON p.brand_id = b.id
    LEFT JOIN 
        product_variants v ON p.id = v.product_id
    LEFT JOIN (   
        SELECT
        product_id,
        SUM(stock_quantity) AS total_stock_quantity
    FROM
        product_variants
    GROUP BY
        product_id
    ) AS sq ON
        p.id = sq.product_id
    LEFT JOIN (
        SELECT
            pim.product_id,
            pim.image_url
        FROM
            product_images pim
        LEFT JOIN image_types it ON
            pim.image_type_id = it.id
        WHERE
            it.name = 'Main'
    ) AS img ON
        p.id = img.product_id
    WHERE p.category_id = %s
    ORDER BY p.id;
    """
    
    cursor.execute(sql, (category_id,))
    products = cursor.fetchall()
    return products


# get all products
def get_product_variants():
    cursor = get_cursor()
    sql = """SELECT
        v.product_id,
        s.size_name,
        c.color_name 
    FROM
        product_variants v
    LEFT JOIN
        sizes s ON v.size_id = s.id
    LEFT JOIN 
        product_colors c ON v.color_id = c.id 
    GROUP BY
        v.product_id,
        s.size_name,
        c.color_name
    ORDER BY v.product_id, s.size_name, c.color_name;
    """
    cursor.execute(sql)
    product_variants = cursor.fetchall()
    return product_variants


def get_best_discount(product_id):
    dbconn = get_cursor()
    discount_rate = 1
    today = datetime.today().date()
        # Fetch discount for the specific product
    dbconn.execute("""
        SELECT MAX(p.discount_rate)
        FROM promotions p
        JOIN promotion_products pp ON p.id = pp.promotion_id
        WHERE pp.product_id = %s AND %s BETWEEN p.start_date AND p.end_date
    """, (product_id,today))
    product_discount = dbconn.fetchone()[0]

    if product_discount is not None:
        discount_rate = float(1 - product_discount)

        return discount_rate

    # Fetch subcategory id for the product
    dbconn.execute("""
        SELECT c.id, c.parent_category_id
        FROM categories c
        JOIN products p ON p.category_id = c.id
        WHERE p.id = %s
    """, (product_id,))
    category_data = dbconn.fetchone()
    if not category_data:
        return discount_rate

    subcategory_id = category_data[0]
    parent_category_id = category_data[1]

    # Fetch discount for the subcategory
    dbconn.execute("""
        SELECT MAX(p.discount_rate)
        FROM promotions p
        JOIN promotion_products pp ON p.id = pp.promotion_id
        WHERE pp.category_id = %s AND %s BETWEEN p.start_date AND p.end_date
    """, (subcategory_id, today))
    subcategory_discount = dbconn.fetchone()[0]

    if subcategory_discount is not None:
        discount_rate = float(1 - subcategory_discount)
        return discount_rate

    # Fetch discount for the parent category
    if parent_category_id:
        dbconn.execute("""
            SELECT MAX(p.discount_rate)
            FROM promotions p
            JOIN promotion_products pp ON p.id = pp.promotion_id
            WHERE pp.category_id = %s AND %s BETWEEN p.start_date AND p.end_date
        """, (parent_category_id,today))
        parent_category_discount = dbconn.fetchone()[0]

        if parent_category_discount is not None:
            discount_rate = float(1 - parent_category_discount)
            return discount_rate

    return discount_rate
