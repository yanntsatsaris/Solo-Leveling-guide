from flask import Flask, render_template

def guides(app: Flask):
    @app.route('/guides')
    def inner_guides():
        return render_template('guides.html')