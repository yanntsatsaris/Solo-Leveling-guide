from flask import Flask, render_template

def game_contents(app: Flask):
    @app.route('/game-contents')
    def inner_game_contents():
        return render_template('game_contents.html')