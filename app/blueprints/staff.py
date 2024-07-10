import re
from config import get_cursor
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, redirect, url_for, request, flash, session

staff = Blueprint(
    'staff',
    __name__,
    static_folder='static',
    template_folder='templates'
)


@staff.route('/')
def staff_dashboard():

    return redirect(url_for('home'))