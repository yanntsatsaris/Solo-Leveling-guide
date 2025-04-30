
from flask import Flask
from routes.RouteHome import home
from routes.RouteGame_contents import game_contents
from routes.RouteCharacters import characters
from routes.RouteGuides import guides
from routes.RouteSJW import SJW

from static.Controleurs.ControleurLog import write_log

app = Flask(__name__, static_folder='static')

write_log("Application started")
# Enregistrer les routes
home(app)
game_contents(app)
characters(app)
guides(app)
SJW(app)

if __name__ == '__main__':
    app.run(debug=True)
