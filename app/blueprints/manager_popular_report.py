from flask import Blueprint, request
from ..controllers.manager_popular_report_controller import report

manager_popular_report = Blueprint(
    'manager_popular_report',
    __name__,
    static_folder='static',
    template_folder='templates/manager_popular_report'
)

@manager_popular_report.route('/report')
def show_popular_report():
    period = request.args.get('period', 'month')  # Default to 'month'
    return report(period)


















