from flask import Blueprint, render_template

guides = Blueprint('guides', __name__)

@guides.route('/guides')
def guides_page():
    return render_template('guides.html')