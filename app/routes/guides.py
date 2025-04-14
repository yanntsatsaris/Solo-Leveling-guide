from flask import Flask, render_template

def init_routes(app: Flask):
    @app.route('/guides')
    def guides():
        return render_template('guides.html')