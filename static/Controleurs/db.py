import psycopg2
from flask import g
from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurLog import write_log

def get_db():
    if 'db' not in g:
        conf = ControleurConf()
        database = conf.get_config('PSQL', 'database')
        user = conf.get_config('PSQL', 'user')
        password = conf.get_config('PSQL', 'password')
        write_log("Connexion à la base de données SQL", log_level="DEBUG")
        g.db = psycopg2.connect(
            dbname=database,
            user=user,
            password=password
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        write_log("Fermeture de la connexion SQL", log_level="DEBUG")

def init_app(app):
    app.teardown_appcontext(close_db)
