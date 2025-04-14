import os
import importlib
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Charger dynamiquement toutes les routes depuis le dossier "routes"
    routes_dir = os.path.join(os.path.dirname(__file__), 'routes')
    for filename in os.listdir(routes_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = f"app.routes.{filename[:-3]}"
            module = importlib.import_module(module_name)
            if hasattr(module, 'init_routes'):
                module.init_routes(app)

    return app