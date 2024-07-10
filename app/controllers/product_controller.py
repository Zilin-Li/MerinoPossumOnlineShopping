from ..models import product_model
from ..models import product_detail_model
from ..models import cart_model
from random import SystemRandom
from decimal import Decimal, ROUND_HALF_UP

#--------------------- product_model------------------------------------
def get_all_products():
    """
    Get all products
    """
    return product_model.get_products()

def get_products_by_category(category_id):
    """
    Get all products
    """
    return product_model.get_products_by_category(category_id)


# format product details
def format_product_details(products, discount_rate):
    products_dicts = []
    for product in products:
        product_dict = {
            'product_id': product[0],
            'product_name': product[1],
            'total_stock_quantity': product[2],
            'product_description': product[3],
            'base_price': float(product[4]),
            'additional_price': float(product[5]) if product[5] is not None else 0,
            'is_active': product[6],
            'category_name': product[7],
            'brand_name': product[8],
            'image_url': product[9],
            'image_type': product[10],
            'description': product[11]
        }
        # Calculate discounted price
        product_dict['discounted_price'] = "{:.2f}".format(round(product_dict['base_price'] * discount_rate, 2))
        product_dict['discounted_price'] = Decimal(product_dict['discounted_price']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        product_dict['base_price'] = Decimal(product_dict['base_price']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        products_dicts.append(product_dict)
    return products_dicts

def get_all_product_variants():
    """
    Get all products
    """
    return product_model.get_product_variants()

def format_product_details_for_customer(products):
    products_dicts = []
    discount_rate =1
    for product in products:
        product_dict = {
            'product_id': product[0],
            'product_name': product[1],
            'total_stock_quantity': product[2],
            'product_description': product[3],
            'base_price': float(product[4]),
            'additional_price': float(product[5]) if product[5] is not None else 0,
            'is_active': product[6],
            'category_name': product[7],
            'brand_name': product[8],
            'image_url': product[9],
            'image_type': product[10],
            'description': product[11]
        }
        discount_rate = get_best_discount(product_dict['product_id'])
        # print(product_dict['base_price']*discount_rate)
        # print(discount_rate)
        
        product_dict['discounted_price'] = "{:.2f}".format(round(product_dict['base_price'] * discount_rate, 2))
        product_dict['discounted_price'] = Decimal(product_dict['discounted_price']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        product_dict['base_price'] = Decimal(product_dict['base_price']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # print(product_dict['discounted_price'] ==  product_dict['base_price'])
    
        products_dicts.append(product_dict)

    return products_dicts

def get_best_discount(product_id):
    """
    Get best discount rate for a product
    """
    return product_model.get_best_discount(product_id)
#--------------------- product_detail_model------------------------------------
def get_main_product_image(productID):
    """
    Get product information detail by productID
    """
    return product_detail_model.get_main_product_image(productID) 

def get_product_color_images(productID):
    """
    Get product variants by productID
    """
    return product_detail_model.get_product_color_images(productID)

def get_product_sizes(productID):
    """
    Get product size by productID
    """
    return product_detail_model.get_product_size(productID)

def get_product_colors(productID):
    """
    Get product color by productID
    """
    return product_detail_model.get_product_color(productID)

def get_product_details_by_id(productID):
    """
    Get product detail by productID
    """
    return product_detail_model.get_product_detail_by_id(productID)
    
# get a specific product detail
def get_product_complete_detail(productID, discount_rate):
    # Fetch all the necessary details using your defined functions
    product_main_image = get_main_product_image(productID)
    product_color_images = get_product_color_images(productID)
    product_sizes = get_product_sizes(productID)
    # product_colors = get_product_colors(productID)
    product_info = get_product_details_by_id(productID)
    
    base_price =  float(product_info[5]) 
   
    discout_price = "{:.2f}".format(round(base_price * discount_rate, 2))
    
    # Combine all the fetched data into a single dictionary
    product_data = {
        'product_info': product_info,
        'main_image': product_main_image,
        'color_images': product_color_images,
        'sizes': product_sizes,
        'discounted_price': discout_price
    }
    return product_data

def get_product_complete_detail_for_customer(productID):
    discount_rate=1
    # Fetch all the necessary details using your defined functions
    product_main_image = get_main_product_image(productID)
    product_color_images = get_product_color_images(productID)
    product_sizes = get_product_sizes(productID)
    # product_colors = get_product_colors(productID)
    product_info = get_product_details_by_id(productID)
    
    base_price =  float(product_info[5]) 

    discount_rate = get_best_discount(productID)
    discounted_price = "{:.2f}".format(round(base_price * discount_rate, 2))
    discounted_price= Decimal(discounted_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    base_price= Decimal(base_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Combine all the fetched data into a single dictionary
    product_data = {
        'product_info': product_info,
        'main_image': product_main_image,
        'color_images': product_color_images,
        'sizes': product_sizes,
        'discounted_price': discounted_price,
        'base_price': base_price
    }
    print(product_data)
    return product_data

def get_product_variant( product_id, color, size):
    """
    Get product variant by productID, color, size
    """
    return product_detail_model.get_product_variant(product_id, color, size)

def get_or_create_cart(user_id):
    """
    Get or create cart by userID
    """
    return product_detail_model.get_or_create_cart(user_id)

def process_cart_item(cart_id, product_id, product_variant, quantity, price):
    """
    Process cart item
    """
    return product_detail_model.process_cart_item(cart_id, product_id, product_variant, quantity, price)
    
    

def generate_card_number(length):   
    number = ''.join(SystemRandom().choice('0123456789') for _ in range(length - 1))
    return number + luhn_checksum(number)

def luhn_checksum(number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return str((10 - checksum % 10) % 10)
    