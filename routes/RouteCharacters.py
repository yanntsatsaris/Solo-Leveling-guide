from flask import Flask, render_template

def characters(app: Flask):
    @app.route('/characters')
    def inner_characters():
        return render_template('characters.html')