from flask import Blueprint, render_template, redirect, url_for, request, flash
from config import get_cursor
from ..controllers.user_controllers import get_session_info
import math


# SCRUM-24 staff manage inventory by Danfeng
staff_manage_inventory = Blueprint(
    'staff_manage_inventory',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# staff displays inventory and change quantity
@staff_manage_inventory.route('/',methods=['GET','POST'] )
def display_inventory():
    is_login, user_id, role_id, discount_rate = get_session_info()
    if not is_login or role_id != 3:
        flash('Please log in first', 'info')
        return redirect(url_for('users.login'))
    else:
        if request.method == 'POST':
            variant_id = request.form.get('variant_id', '')
            stock_quantity = request.form.get('stock_quantity', '')  
            try:
                stock_quantity = int(stock_quantity)
                if stock_quantity >= 0:  
                    try:    
                        cursor = get_cursor() 
                        cursor.execute("UPDATE product_variants SET stock_quantity = %s WHERE id = %s", (stock_quantity, variant_id))
                        flash(f'Update stock quantity for product variant {variant_id} successfully. Its new stock quantity is {stock_quantity}.', 'success')
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        flash('An error occurred. Please try again later.', 'danger')  
                else:
                    flash('Stock quantity must be greater than or equal to zero.', 'danger')
            except ValueError:
                flash('Stock quantity must be an integer.', 'danger')
    
        name = request.args.get('name')
        quantity = request.args.get('quantity')
        variant_id = request.args.get('variant_id')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        query = """
            SELECT pv.id, product_name, color_name, size_name, stock_quantity
            FROM product_variants pv 
            JOIN products p ON pv.product_id=p.id
            JOIN product_colors pc ON pv.color_id=pc.id
            JOIN sizes s ON pv.size_id=s.id
            WHERE 1=1
        """
        params = []

        if name:
            query += " AND product_name LIKE %s"
            params.append(f"%{name}%")

        if quantity:
            query += " AND stock_quantity = %s"
            params.append(quantity)

        if variant_id:
            query += " AND pv.id = %s"
            params.append(variant_id)
            
        query += " ORDER BY stock_quantity"
        
        inventory_list = []
        dbconn = get_cursor()
        try:
            # Get the total number of inventory items
            dbconn.execute(f"SELECT COUNT(*) FROM ({query}) AS total", tuple(params))
            total_inventory = dbconn.fetchone()[0]
            
            # Pagination calculations
            total_pages = math.ceil(total_inventory / per_page)
            offset = (page - 1) * per_page
            
            # Get the paginated inventory items
            paginated_query = query + " LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            dbconn.execute(paginated_query, tuple(params))
            inventory_list = dbconn.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred. Please try again later.', 'danger')
        
        if quantity and not inventory_list:
            flash("No inventory found for the quantity.", "error")

        if name and not inventory_list:
            flash("No inventory found for the name.", "error")

        if variant_id and not inventory_list:
            flash("No inventory found for the variant id.", "error")
        
        return render_template(
            '/staff_manage_inventory/staff_manage_inventory.html',
            inventory_list=inventory_list,
            page=page,
            total_pages=total_pages
        )





