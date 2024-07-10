from flask import render_template
from datetime import datetime
from ..models.manager_popular_report_model import get_popular_products_report

def report(period):
    # Determine the date range based on the selected period
    end_date = datetime.now()
    if period == 'month':
        start_date = end_date.replace(day=1)
    elif period == 'quarter':
        quarter = (end_date.month - 1) // 3 + 1
        start_date = end_date.replace(month=3 * (quarter - 1) + 1, day=1)
    elif period == 'year':
        start_date = end_date.replace(month=1, day=1)
    else:
        # Default to month if invalid period
        start_date = end_date.replace(day=1)

    start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

    report_data = get_popular_products_report(start_date, end_date)
    
    return render_template('manager_popular_report/manager_popular_report.html', report_data=report_data, period=period)















    

