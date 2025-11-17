from flask import Flask, session, redirect, request
from flask_login import LoginManager

from routes.RouteHome import home_bp
from routes.RouteGame_contents import game_contents_bp
from routes.RouteCharacters import characters_bp
from routes.RouteGuides import guides_bp
from routes.RouteSJW import sjw_bp
from routes.RouteUsers import users_bp
from routes.RouteAdmin import admin_bp

# Importer le contrôleur de configuration
from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.ControleurUser import user_loader
from static.Controleurs import db

app = Flask(__name__)
conf = ControleurConf()
app.secret_key = conf.get_config('APP', 'secret_key')
db.init_app(app)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(user_loader)

write_log("Application démarrée", log_level="INFO")

@app.route('/set-language', methods=['POST'])
def set_language():
    # Récupérer la langue sélectionnée dans le formulaire
    language = request.form.get('language')
    if language in ['FR-fr', 'EN-en']:
        session['language'] = language  # Stocker la langue dans la session
    return redirect(request.referrer or '/')  # Rediriger vers la page précédente

# Enregistrer les routes
app.register_blueprint(home_bp)
app.register_blueprint(game_contents_bp)
app.register_blueprint(characters_bp)
app.register_blueprint(guides_bp)
app.register_blueprint(sjw_bp)
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)


if __name__ == '__main__':
    app.run(debug=True, port=int(conf.get_config('APP', 'port')))
