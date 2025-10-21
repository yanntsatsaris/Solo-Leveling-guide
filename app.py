from flask import Flask, session, redirect, request
from flask_login import LoginManager

# Import Blueprints
from routes.RouteHome import home_bp
from routes.RouteGame_contents import game_contents_bp
from routes.RouteGuides import guides_bp
from routes.RouteUsers import users_bp
from routes.RouteAdmin import admin_bp
from routes.characters_public import characters_public_bp
from routes.characters_admin import characters_admin_bp
from routes.sjw_public import sjw_public_bp
from routes.sjw_admin import sjw_admin_bp

from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.ControleurUser import user_loader

app = Flask(__name__)
conf = ControleurConf()
app.secret_key = conf.get_config('APP', 'secret_key')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(user_loader)

write_log("Application démarrée", log_level="INFO")

@app.route('/set-language', methods=['POST'])
def set_language():
    language = request.form.get('language')
    if language in ['FR-fr', 'EN-en']:
        session['language'] = language
    return redirect(request.referrer or '/')

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(game_contents_bp)
app.register_blueprint(guides_bp)
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(characters_public_bp)
app.register_blueprint(characters_admin_bp)
app.register_blueprint(sjw_public_bp)
app.register_blueprint(sjw_admin_bp)

if __name__ == '__main__':
    app.run(debug=True, port=int(conf.get_config('APP', 'port')))
