from config import get_cursor
from flask import Blueprint, render_template, redirect, url_for, request, flash, session


staff_product = Blueprint(
    'staff_product',
    __name__,
    static_folder='static',
    template_folder='templates'
)


@staff_product.route('/categories', methods=['GET', 'POST'])
def list_categories():
    dbconn = get_cursor()

    # 获取所有促销活动
    dbconn.execute("SELECT id, promotion_name FROM promotions")
    promotions = dbconn.fetchall()

    # 获取所有分类
    dbconn.execute("SELECT id, category_name, description FROM categories")
    categories = dbconn.fetchall()

    if request.method == 'POST':
        for category in categories:
            category_id = category[0]
            selected_promotion_id = request.form.get(
                f'promotion_{category_id}')
            if selected_promotion_id:
                dbconn.execute(
                    "SELECT * FROM promotion_products WHERE category_id = %s", (category_id,))
                promotion_product = dbconn.fetchone()
                dbconn.fetchall()  # 确保读取所有结果

                if promotion_product:
                    dbconn.execute(
                        "UPDATE promotion_products SET promotion_id = %s WHERE category_id = %s",
                        (selected_promotion_id, category_id)
                    )
                else:
                    dbconn.execute(
                        "INSERT INTO promotion_products (promotion_id, category_id) VALUES (%s, %s)",
                        (selected_promotion_id, category_id)
                    )

        flash('Categories have been updated with the selected promotions.', 'success')
        return redirect(url_for('staff_product.list_categories'))

    return render_template('staff_product/staff_product.html', promotions=promotions, categories=categories)
