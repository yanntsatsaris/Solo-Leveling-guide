from flask import Flask, render_template

def register_routes(app: Flask):
    @app.route('/characters')
    def characters():
        return render_template('characters.html')