from flask import Flask

def create_app():
    app = Flask(__name__)

    # Importer et enregistrer les Blueprints
    from app.routes.home import home
    from app.routes.game_contents import game_contents
    from app.routes.characters import characters
    from app.routes.guides import guides

    app.register_blueprint(home)
    app.register_blueprint(game_contents)
    app.register_blueprint(characters)
    app.register_blueprint(guides)

    return app