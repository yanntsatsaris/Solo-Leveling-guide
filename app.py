from flask import Flask, session, redirect, request
from flask_login import LoginManager

from routes.RouteHome import home
from routes.RouteGame_contents import game_contents
from routes.RouteCharacters import characters
from routes.RouteGuides import guides
from routes.RouteSJW import SJW
from routes.RouteUsers import users

# Importer le contrôleur de configuration
from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.ContoleurUser import user_loader

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
characters(app)
guides(app)
SJW(app)
users(app)


if __name__ == '__main__':
    app.run(debug=True, port=int(conf.get_config('APP', 'port')))
