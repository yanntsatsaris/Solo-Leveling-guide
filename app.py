import sys
import logging
from flask import Flask
from routes.RouteHome import home
from routes.RouteGame_contents import game_contents
from routes.RouteCharacters import characters
from routes.RouteGuides import guides
from routes.RouteSJW import SJW

# Rediriger stdout et stderr vers Gunicorn
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
sys.stdout = sys.stderr

app = Flask(__name__, static_folder='static')

# Enregistrer les routes
home(app)
game_contents(app)
characters(app)
guides(app)
SJW(app)

if __name__ == '__main__':
    app.run(debug=True)
