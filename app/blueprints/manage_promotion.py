import datetime
from flask import request, redirect, url_for, flash
from config import get_cursor
from flask import Blueprint, render_template, redirect, url_for, request, flash, session


manage_promotion = Blueprint(
    'manage_promotion',
    __name__,
    static_folder='static',
    template_folder='templates'
)


@manage_promotion.route('/add', methods=['GET', 'POST'])
def add_promotion():
    # check if current user is manager
    if session.get('role_id') == 3:
        if request.method == 'POST':
            # get form data
            promotion_name = request.form.get('promotion_name')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            discount_rate = request.form.get('discount_rate')
            description = request.form.get('description')

            # validate date format
            try:
                start_date = datetime.datetime.strptime(
                    start_date, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(
                    end_date, '%Y-%m-%d').date()
                today = datetime.date.today()
                # Check if start date is after today's date
                if start_date <= today:
                    flash('Start date must be after today.', 'error')
                    return redirect(url_for('manage_promotion.add_promotion'))
                # start data < end data
                if start_date > end_date:
                    flash('Start date must be earlier than end date.', 'error')
                    return redirect(url_for('manage_promotion.add_promotion'))
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
                return redirect(url_for('manage_promotion.add_promotion'))

            try:
                discount_rate = float(discount_rate)
                if discount_rate < 0:
                    flash('Discount rate must be greater than or equal to 0.', 'error')
                    return redirect(url_for('manage_promotion.add_promotion'))
            except ValueError:
                flash('Invalid discount rate. Please enter a valid number.', 'error')
                return redirect(url_for('manage_promotion.add_promotion'))

            # connect to database
            dbconn = get_cursor()
            dbconn.execute("""
                INSERT INTO promotions (promotion_name, start_date, end_date, discount_rate, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (promotion_name, start_date, end_date, discount_rate, description))
            flash('Promotion added successfully!', 'success')
            return redirect(url_for('manage_promotion.promotion'))

        return render_template('promotion/add_promotion.html')
    else:
        return "Unauthorized", 403


@manage_promotion.route('/')
def promotion():
    # check if current user is manager
    if session.get('role_id') == 3:
        # connect to database
        dbconn = get_cursor()
        # get all promotion information
        dbconn.execute(
            "SELECT id, promotion_name, start_date, end_date, discount_rate, description, is_active FROM promotions")
        promotions = dbconn.fetchall()

        # store promotion information in a list of dictionaries
        promotions = [
            {
                'id': row[0],
                'promotion_name': row[1],
                'start_date': row[2],
                'end_date': row[3],
                'discount_rate': row[4],
                'description': row[5],
                'is_active': row[6]
            }
            for row in promotions
        ]

        return render_template('promotion/manage_promotion.html', promotions=promotions)
    else:
        return "Unauthorized", 403


@manage_promotion.route('/edit/<int:promotion_id>', methods=['GET', 'POST'])
def edit_promotion(promotion_id):
    # check if current user is manager
    if session.get('role_id') == 3:
        dbconn = get_cursor()
        # get promotion information by id
        dbconn.execute(
            "SELECT id, promotion_name, start_date, end_date, discount_rate, description, is_active FROM promotions WHERE id = %s", (promotion_id,))
        row = dbconn.fetchone()

        # store promotion information in a dictionary
        promotion = {
            'id': row[0],
            'promotion_name': row[1],
            'start_date': row[2],
            'end_date': row[3],
            'discount_rate': row[4],
            'description': row[5],
            'is_active': row[6]
        }

        if request.method == 'POST':
            # get form data
            promotion_name = request.form.get('promotion_name')
            # start_date = request.form.get('start_date')
            # end_date = request.form.get('end_date')
            discount_rate = request.form.get('discount_rate')
            description = request.form.get('description')
            is_active = request.form.get('is_active') == 'on'

            # validate form data
            # try:
                # start_date = datetime.datetime.strptime(
                #     start_date, '%Y-%m-%d').date()
                # end_date = datetime.datetime.strptime(
                #     end_date, '%Y-%m-%d').date()
                # today = datetime.date.today()

                # Check if start date is after today's date
            #     if start_date <= today:
            #         flash('Start date must be after today.', 'error')
            #         return redirect(url_for('manage_promotion.edit_promotion', promotion_id=promotion_id))

            #     if start_date > end_date:
            #         flash('Start date must be before end date.', 'error')
            #         return redirect(url_for('manage_promotion.edit_promotion', promotion_id=promotion_id))

            # except ValueError:
            #     flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            #     return redirect(url_for('manage_promotion.edit_promotion', promotion_id=promotion_id))


            try:
                discount_rate = float(discount_rate)
                if discount_rate < 0:
                    flash('Discount rate must be greater than or equal to 0.', 'error')
                    return redirect(url_for('manage_promotion.add_promotion'))
            except ValueError:
                flash('Invalid discount rate. Please enter a valid number.', 'error')
                return redirect(url_for('manage_promotion.add_promotion'))

            # update promotion information in the database
            dbconn.execute("""
                UPDATE promotions
                SET promotion_name = %s,  discount_rate = %s, description = %s, is_active = %s
                WHERE id = %s
            """, (promotion_name, discount_rate, description, is_active, promotion_id))
            flash('Promotion updated successfully!', 'success')
            return redirect(url_for('manage_promotion.promotion'))

        return render_template('promotion/edit_promotion.html', promotion=promotion)
    else:
        return "Unauthorized", 403


@manage_promotion.route('/delete/<int:promotion_id>', methods=['POST'])
def delete_promotion(promotion_id):
    # check if current user is manager
    if session.get('role_id') == 3:
        dbconn = get_cursor()
        # delete promotion from database
        dbconn.execute("DELETE FROM promotions WHERE id = %s", (promotion_id,))
        flash('Promotion deleted successfully!', 'success')
        return redirect(url_for('manage_promotion.promotion'))
    else:
        return "Unauthorized", 403