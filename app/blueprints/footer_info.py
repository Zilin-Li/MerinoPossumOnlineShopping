import re
from config import get_cursor
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, redirect, url_for, request, flash, session


footer_info = Blueprint(
    'footer_info',
    __name__,
    static_folder='static',
    template_folder='templates'
)


# Define routes for footer pages
@footer_info.route('/contact_info')
def contact_info():
    return render_template('footer_info/contact_info.html')

@footer_info.route('/delivery_info')
def delivery_info():
    return render_template('footer_info/delivery_info.html')

@footer_info.route('/returns_policy')
def returns_policy():
    return render_template('footer_info/returns_policy.html')

@footer_info.route('/clothing_size')
def clothing_size():
    return render_template('footer_info/clothing_size.html')