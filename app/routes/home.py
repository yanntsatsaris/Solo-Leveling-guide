from flask import Flask, render_template

def register_routes(app: Flask):
    @app.route('/')
    def home():
        return render_template('index.html')