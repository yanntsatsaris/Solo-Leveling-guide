from flask import Flask, session, redirect, request
from flask_login import LoginManager

from routes.RouteHome import home
from routes.RouteGame_contents import game_contents
from routes.RouteGuides import guides
from routes.RouteUsers import users
from routes.sjw_public import sjw_public_routes
from routes.sjw_admin import sjw_admin_routes
from routes.characters_public import characters_public_routes
from routes.characters_admin import characters_admin_routes
from routes.RouteAdmin import admin_routes

# Importer le contrôleur de configuration
from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.ControleurUser import user_loader

app = Flask(__name__)
conf = ControleurConf()
app.secret_key = conf.get_config('APP', 'secret_key')

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
home(app)
game_contents(app)
guides(app)
users(app)
sjw_public_routes(app)
sjw_admin_routes(app)
characters_public_routes(app)
characters_admin_routes(app)
admin_routes(app)


if __name__ == '__main__':
    app.run(debug=True, port=int(conf.get_config('APP', 'port')))
