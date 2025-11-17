from flask import Blueprint, render_template

guides_bp = Blueprint('guides', __name__)

@guides_bp.route('/guides')
def inner_guides():
    return render_template('guides.html')