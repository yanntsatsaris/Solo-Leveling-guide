from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def inner_home():
    return render_template('index.html')
