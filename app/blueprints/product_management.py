from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.product_controller import get_all_product_variants
from config import get_cursor
from ..models.product_management_model import add_variant, check_product_image, check_variant, clear_variant_quantity, delete_product_main_image, edit_product_image, get_all_categories, get_all_products, get_all_products_variants, get_all_sizes, get_product_by_id, add_product, update_product, delete_product, get_product_images_with_details, add_product_image, delete_product_image, get_all_brands, get_all_image_types, get_all_colors, update_variant
import math

product_management = Blueprint(
    'product_management',
    __name__,
    static_folder='static',
    template_folder='templates'
)


@product_management.route('/products', methods=['GET'])
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    products = get_all_products()

    product_variants = get_all_products_variants()
    product_data = {product['id']: product for product in products}

    # Adding an empty list to hold variants for each product
    for product in product_data.values():
        product['variants'] = []

    # Associating product variants with their respective products
    for variant in product_variants:
        product_id = variant['product_id']
        if product_id in product_data:
            product_data[product_id]['variants'].append(variant)

    all_colors = get_all_colors()
    all_sizes = get_all_sizes()
    
    # Pagination calculations
    total_products = len(product_data)
    total_pages = math.ceil(total_products / per_page)
    offset = (page - 1) * per_page
    paginated_products = list(product_data.values())[offset:offset + per_page]

    return render_template(
        'product_management/product_list.html',
        products=paginated_products,
        all_colors=all_colors,
        all_sizes=all_sizes,
        page=page,
        total_pages=total_pages
    )


@product_management.route('/products/add', methods=['GET', 'POST'])
def add_product_view():
    if request.method == 'POST':
        product_data = {
            'product_name': request.form['productName'],
            'category_id': request.form['category'],
            'brand_id': request.form['brand'],
            'description': request.form['description'],
            'base_price': request.form['price'],
            'is_active': '1'
        }
        product_id = add_product(product_data)
        image_url = request.form['main_image']
        if image_url is not None and image_url != '':
            add_product_image(product_id, trim_url(image_url), 1, None, '')
        flash('Product added successfully!', 'success')
        return redirect(url_for('product_management.list_products'))

    all_brands = get_all_brands()
    all_categories = get_all_categories()
    return render_template('product_management/add_product.html', all_brands=all_brands, all_categories=all_categories)


@product_management.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product_view(product_id):
    product = get_product_by_id(product_id)
    if request.method == 'POST':
        product_data = {
            'product_name': request.form['productName'],
            'category_id': request.form['category'],
            'brand_id': request.form['brand'],
            'description': request.form['description'],
            'base_price': request.form['price'],
            'is_active': '1'
        }
        image_url = request.form['main_image']
        # if image_url is none or empty, flash error message if image_url is not valid
        if image_url is None or image_url == '':
            flash('Invalid image URL!', 'error')
            return redirect(url_for('product_management.edit_product_view', product_id=product_id))
        else:
            # if image_url is not none or empty, check if it is a valid image URL
            # if not, flash error message and redirect to the edit page
            if not image_url.startswith('http') or not image_url.endswith(('.jpg', '.jpeg', '.png', '.gif','.webp')):
                flash('Invalid image URL!', 'error')
                return redirect(url_for('product_management.edit_product_view', product_id=product_id))
            else:
                # if image_url is valid, update the product and delete the main image
                # then add the new main image   
                image_url = trim_url(image_url)
               
                update_product(product_id, product_data)
                delete_product_main_image(product_id)
                
                add_product_image(product_id, trim_url(image_url), 1, None, '')
                
                flash('Product updated successfully!', 'success')
                return redirect(url_for('product_management.list_products'))   
    all_brands = get_all_brands()
    all_categories = get_all_categories()
    return render_template('product_management/edit_product.html', product=product, all_brands=all_brands, all_categories=all_categories)


@product_management.route('/products/<int:product_id>/delete', methods=['POST'])
def delete_product_view(product_id):
    delete_product(product_id)
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product_management.list_products'))


@product_management.route('/products/<int:product_id>/images', methods=['GET', 'POST'])
def manage_product_images(product_id):
    if request.method == 'POST':
        image_url = request.form['image_url']
        image_type_id = request.form['image_type']
        color_id = request.form['color']
        description = request.form['description']

        add_product_image(product_id, image_url,
                          image_type_id, color_id, description)
        flash('Image added successfully!', 'success')
        return redirect(url_for('product_management.manage_product_images', product_id=product_id))

    product_images = get_product_images_with_details(product_id)
    image_types = get_all_image_types()
    colors = get_all_colors()
    return render_template('product_management/manage_images.html', product_id=product_id, product_images=product_images, image_types=image_types, colors=colors)


@product_management.route('/products/<int:product_id>/images/<int:image_id>/delete', methods=['POST'])
def delete_product_image_view(product_id, image_id):
    delete_product_image(image_id)
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('product_management.manage_product_images', product_id=product_id))


@product_management.route('/products/variant/add', methods=['POST'])
def add_product_variant():
    product_id = request.form['product_id']
    color_id = request.form['color']
    size_id = request.form['size']
    stock_quantity = request.form.get('quantity', 0)
    additonal_price = request.form.get('price', 0.0)
    if check_variant(product_id, color_id, size_id):
        flash('Product variant already exist!', 'error')
        return redirect(url_for('product_management.list_products'))
    variant_data = {
        'product_id': product_id,
        'color_id': color_id,
        'size_id': size_id,
        'stock_quantity': stock_quantity,
        'additonal_price': additonal_price
    }
    add_variant(variant_data)
    image_url = request.form['variant_image_url']
    if not check_product_image(product_id, color_id) and image_url is not None and image_url != '':
        add_product_image(product_id, trim_url(image_url), 3, color_id, '')
    flash('Product variant added successfully!', 'success')
    return redirect(url_for('product_management.list_products'))


@product_management.route('/products/variant/edit', methods=['POST'])
def edit_product_variant():
    product_id = request.form['product_id']
    variant_id = request.form['variant_id']
    color_id = request.form['color']
    size_id = request.form['size']
    stock_quantity = request.form.get('quantity', 0)
    additonal_price = request.form.get('price', 0.0)
    variant_data = {
        'id': variant_id,
        'color_id': color_id,
        'size_id': size_id,
        'stock_quantity': stock_quantity,
        'additonal_price': additonal_price
    }
    update_variant(variant_data)
    image_url = request.form['variant_image_url']
    if image_url is not None and image_url != '':
        if check_product_image(product_id, color_id):
            edit_product_image(trim_url(image_url), product_id, color_id)
        else:    
            add_product_image(product_id, trim_url(image_url), 3, color_id, '')
    flash('Product variant added successfully!', 'success')
    return redirect(url_for('product_management.list_products'))


@product_management.route('/products/variant/<int:product_id>/<int:variant_id>/delete', methods=['POST'])
def delete_variant_view(product_id, variant_id):
    clear_variant_quantity(product_id, variant_id)
    flash('Action successfully!', 'success')
    return redirect(url_for('product_management.list_products'))

def trim_url(url):
    # Split the URL at "COMP639S1_Project_2_Group_AK_IMGS/main/" and return the part after it
    return url.split("COMP639S1_Project_2_Group_AK_IMGS/main/")[-1]