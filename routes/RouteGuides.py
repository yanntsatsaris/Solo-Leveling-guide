from flask import Blueprint, render_template

guides_bp = Blueprint('guides', __name__, url_prefix='/guides')

@guides_bp.route('/')
def inner_guides():
    return render_template('guides.html')
