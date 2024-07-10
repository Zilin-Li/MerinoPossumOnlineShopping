# app/models/product_management_model.py
from config import get_cursor


def get_all_products():
    cursor = get_cursor()
    cursor.execute("""SELECT
        p.id,
        p.product_name,
        p.category_id,
        p.brand_id,
        p.description,
        p.base_price,
        p.is_active,
        COALESCE(img.image_url, 'image-not-found.jpg') AS image_url,
        c.category_name,
        b.brand_name,
        COALESCE(sq.total_stock_quantity, 0) AS total_stock_quantity
    FROM
        products p
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
    LEFT JOIN 
            categories c ON
        p.category_id = c.id
    LEFT JOIN 
            brands b ON
        p.brand_id = b.id
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
    order by p.is_active desc, p.id desc              
                   """)
    products = cursor.fetchall()
    products = [{'id': row[0], 'product_name': row[1], 'category_id': row[2], 'brand_id': row[3],
                 'description': row[4], 'base_price': row[5], 'is_active': row[6], 'image_url': row[7],
                 'category_name': row[8], 'brand_name': row[9], 'stock_quantity': row[10]
                 } for row in products]
    return products

def get_all_products_variants():
    cursor = get_cursor()
    cursor.execute("""SELECT pv.*, s.*, pc.*, COALESCE(pim.image_url, 'image-not-found.jpg') AS image_url
        from product_variants pv
        LEFT JOIN sizes s on
            s.id = pv.size_id 
        LEFT JOIN product_colors pc ON
        pc.id = pv.color_id 
        LEFT JOIN product_images pim ON
        pim.product_id = pv.product_id and pim.color_id = pv.color_id 
        order by pv.product_id desc             
                   """)
    product_variants = cursor.fetchall()
    product_variants = [{'id': row[0], 'product_id': row[1], 'color_id': row[2], 'size_id': row[3],
                 'stock_quantity': row[4], 'additonal_price': row[5], 'size_name': row[7], 'color_name': row[9], 'image_url': row[10]
                 } for row in product_variants]
    return product_variants

def get_product_by_id(product_id):
    cursor = get_cursor()
    cursor.execute(""" SELECT
        p.id, p.product_name, p.category_id, p.brand_id, p.description, p.base_price, COALESCE(img.image_url, 'image-not-found.jpg') AS image_url
    FROM
        products p
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
    LEFT JOIN 
            categories c ON
        p.category_id = c.id
    LEFT JOIN 
            brands b ON
        p.brand_id = b.id
    where p.id = %s""", (product_id,))
    product = cursor.fetchone()
    return product


def add_product(product_data):
    cursor = get_cursor()
    sql = """
        INSERT INTO products (product_name, category_id, brand_id, description, base_price, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        product_data['product_name'],
        product_data['category_id'],
        product_data['brand_id'],
        product_data['description'],
        product_data['base_price'],
        product_data['is_active']
    )
    cursor.execute(sql, values)
    return cursor.lastrowid


def add_product_image(product_id, image_url, image_type_id, color_id, description):
    cursor = get_cursor()
    sql = """
        INSERT INTO product_images (product_id, image_url, image_type_id, color_id, description) 
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (product_id, image_url, image_type_id, color_id, description)
    cursor.execute(sql, values)


def update_product(product_id, product_data):
    cursor = get_cursor()
    sql = """
        UPDATE products
        SET product_name = %s, category_id = %s, brand_id = %s, description = %s, base_price = %s, is_active = %s
        WHERE id = %s
    """
    values = (
        product_data['product_name'],
        product_data['category_id'],
        product_data['brand_id'],
        product_data['description'],
        product_data['base_price'],
        product_data['is_active'],
        product_id
    )
    cursor.execute(sql, values)


def delete_product(product_id):
    cursor = get_cursor()
    cursor.execute("UPDATE products SET is_active = 0 WHERE id = %s", (product_id,))


def get_product_images_with_details(product_id):
    cursor = get_cursor()
    cursor.execute("""
        SELECT pi.id, pi.image_url, pi.description, it.name AS image_type_name, pc.color_name
        FROM product_images pi
        JOIN image_types it ON pi.image_type_id = it.id
        JOIN product_colors pc ON pi.color_id = pc.id
        WHERE pi.product_id = %s
    """, (product_id,))
    product_images = cursor.fetchall()
    product_images = [{'id': row[0], 'image_url': row[1], 'description': row[2],
                       'image_type_name': row[3], 'color_name': row[4]}
                      for row in product_images]
    return product_images


def add_product_image(product_id, image_url, image_type_id, color_id, description):
    cursor = get_cursor()
    sql = """
        INSERT INTO product_images (product_id, image_url, image_type_id, color_id, description)
        VALUES (%s, %s, %s, %s, %s)  
    """
    values = (product_id, image_url, image_type_id, color_id, description)
    cursor.execute(sql, values)

def edit_product_image(image_url, product_id, color_id):
    cursor = get_cursor()
    sql = """
        UPDATE product_images set image_url = %s WHERE product_id = %s and color_id = %s
    """
    values = (image_url, product_id, color_id)
    cursor.execute(sql, values)

def delete_product_main_image(product_id):
    cursor = get_cursor()
    cursor.execute("DELETE FROM product_images WHERE product_id = %s and image_type_id = 1", (product_id,))

def delete_product_image(product_id, color_id):
    cursor = get_cursor()
    cursor.execute("DELETE FROM product_images WHERE product_id = %s and color_id = %s and image_type_id <> 1", (product_id, color_id,))

def delete_product_image_by_id(image_id):
    cursor = get_cursor()
    cursor.execute("DELETE FROM product_images WHERE id = %s", (image_id,))

def check_product_image(product_id, color_id):
    cursor = get_cursor()
    cursor.execute("SELECT count(1) from product_images where product_id = %s and color_id = %s", (product_id, color_id,))
    variants = cursor.fetchall()
    return variants[0][0] > 0

# 你可以根据需要添加更多的函数来处理图片上传等操作


def get_all_image_types():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM image_types")
    image_types = cursor.fetchall()
    image_types = [{'id': row[0], 'name': row[1],
                    'description': row[2]} for row in image_types]
    return image_types


def get_all_colors():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM product_colors")
    colors = cursor.fetchall()
    colors = [{'id': row[0], 'name': row[1]} for row in colors]
    return colors


def get_all_brands():
    cursor = get_cursor()
    cursor.execute("SELECT id, brand_name FROM brands WHERE brand_name <> ''")
    brands = cursor.fetchall()
    brands = [{'id': brand[0], 'name': brand[1]} for brand in brands]
    return brands


def get_all_sizes():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM sizes")
    sizes = cursor.fetchall()
    sizes = [{'id': size[0], 'name': size[1]} for size in sizes]
    return sizes


def get_all_categories():
    cursor = get_cursor()
    cursor.execute("SELECT id, category_name FROM categories")
    categories = cursor.fetchall()
    categories = [{'id': category[0], 'name': category[1]} for category in categories]
    return categories


def check_variant(product_id, color_id, size_id):
    cursor = get_cursor()
    cursor.execute("SELECT count(1) from product_variants where product_id = %s and color_id = %s and size_id = %s", (product_id,color_id, size_id,))
    variants = cursor.fetchall()
    return variants[0][0] > 0


def add_variant(variant_data):
    cursor = get_cursor()
    sql = """
        INSERT INTO product_variants (product_id,color_id,size_id,stock_quantity,additonal_price)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        variant_data['product_id'],
        variant_data['color_id'],
        variant_data['size_id'],
        variant_data['stock_quantity'],
        variant_data['additonal_price']
    )
    cursor.execute(sql, values)
    return cursor.lastrowid


def update_variant(variant_data):
    cursor = get_cursor()
    sql = """
        UPDATE product_variants SET color_id = %s, size_id = %s, stock_quantity = %s, additonal_price = %s WHERE id = %s
    """
    values = (
        variant_data['color_id'],
        variant_data['size_id'],
        variant_data['stock_quantity'],
        variant_data['additonal_price'],
        variant_data['id']
    )
    cursor.execute(sql, values)
    return cursor.lastrowid


def clear_variant_quantity(product_id, variant_id):
    cursor = get_cursor()
    cursor.execute("UPDATE product_variants SET stock_quantity = 0 WHERE product_id = %s and id = %s", (product_id,variant_id,))