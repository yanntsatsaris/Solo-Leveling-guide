from flask import Flask, render_template

def game_contents(app: Flask):
    @app.route('/game-contents')
    def inner_game_contents():
        return render_template('game_contents.html')
    
    @app.route('/game-contents/game-modes')
    def game_modes():
        return render_template('game_modes.html')