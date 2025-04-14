from flask import Flask, render_template

def home(app: Flask):
    @app.route('/')
    def inner_home():
        return render_template('index.html')