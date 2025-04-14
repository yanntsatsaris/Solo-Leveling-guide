from flask import Flask
from app.routes.home import register_routes as home_routes
from app.routes.game_contents import register_routes as game_contents_routes
from app.routes.characters import register_routes as characters_routes
from app.routes.guides import register_routes as guides_routes

app = Flask(__name__)

# Enregistrer les routes
home_routes(app)
game_contents_routes(app)
characters_routes(app)
guides_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
