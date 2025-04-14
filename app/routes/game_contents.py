from flask import Flask, render_template

def init_routes(app: Flask):
    @app.route('/game-contents')
    def game_contents():
        return render_template('game_contents.html')