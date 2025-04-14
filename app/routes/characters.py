from flask import Blueprint, render_template

characters = Blueprint('characters', __name__)

@characters.route('/characters')
def characters_page():
    return render_template('characters.html')