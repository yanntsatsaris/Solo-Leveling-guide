from flask import Blueprint, render_template

game_contents_bp = Blueprint('game_contents', __name__, url_prefix='/game-contents')

@game_contents_bp.route('/')
def inner_game_contents():
    return render_template('game_contents.html')

@game_contents_bp.route('/game-modes')
def game_modes():
    return render_template('game_modes.html')
