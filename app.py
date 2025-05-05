from flask import Flask, session, redirect, request
from routes.RouteHome import home
from routes.RouteGame_contents import game_contents
from routes.RouteCharacters import characters
from routes.RouteGuides import guides
from routes.RouteSJW import SJW

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Nécessaire pour utiliser les sessions

session['language'] = 'EN-en'  # Valeur par défaut de la langue

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

if __name__ == '__main__':
    app.run(debug=True)
