from flask import Flask, render_template

def register_routes(app: Flask):
    @app.route('/guides')
    def guides():
        return render_template('guides.html')