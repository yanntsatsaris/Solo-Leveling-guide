from flask import Blueprint, render_template

game_contents = Blueprint('game_contents', __name__)

@game_contents.route('/game-contents')
def game_contents_page():
    return render_template('game_contents.html')