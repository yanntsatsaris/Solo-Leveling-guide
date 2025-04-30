import logging
from flask import Flask
from routes.RouteHome import home
from routes.RouteGame_contents import game_contents
from routes.RouteCharacters import characters
from routes.RouteGuides import guides
from routes.RouteSJW import SJW

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

# Enregistrer les routes
home(app)
game_contents(app)
characters(app)
guides(app)
SJW(app)

if __name__ == '__main__':
    app.run(debug=True)
