from flask import Flask, session, redirect, request, render_template, url_for, flash
from flask_caching import Cache
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer

from extensions import cache
from routes.RouteHome import home_bp
from routes.RouteGame_contents import game_contents_bp
from routes.RouteCharacters import characters_bp
from routes.RouteGuides import guides_bp
from routes.RouteSJW import sjw_bp
from routes.RouteUsers import users_bp
from routes.RouteAdmin import admin_bp
from routes.utils import asset_url_for

# Importer les contrôleurs
from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.ControleurUser import user_loader
from static.Controleurs.ControleurLdap import ControleurLdap
from static.Controleurs.ControleurMail import init_mail, send_password_reset_email
from static.Controleurs import db

app = Flask(__name__)
conf = ControleurConf()
app.secret_key = conf.get_config('APP', 'secret_key')

# Initialiser le sérialiseur pour les jetons
s = URLSafeTimedSerializer(app.secret_key)

# Configuration du cache
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600
cache.init_app(app)

# Initialisation de la base de données
db.init_app(app)

# Initialisation de Flask-Mail
init_mail(app, conf)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(user_loader)

write_log("Application démarrée", log_level="INFO")

@app.context_processor
def inject_asset_url():
    return dict(asset_url_for=asset_url_for)

@app.route('/set-language', methods=['POST'])
def set_language():
    language = request.form.get('language')
    if language in ['FR-fr', 'EN-en']:
        session['language'] = language
    return redirect(request.referrer or '/')

# --- Routes pour la réinitialisation du mot de passe ---

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        uid = request.form.get('uid')
        ldap_controller = ControleurLdap()
        user_info = ldap_controller.get_user_by_uid(uid)

        if user_info and 'mail' in user_info:
            user_email = user_info['mail'][0].decode('utf-8')
            # Générer le jeton
            token = s.dumps(user_email, salt='password-reset-salt')
            # Créer l'URL de réinitialisation
            reset_url = url_for('reset_password', token=token, _external=True)
            # Envoyer l'e-mail
            send_password_reset_email(user_email, reset_url)
            flash("Un e-mail de réinitialisation a été envoyé à votre adresse.", "success")
        else:
            # Message générique pour éviter l'énumération d'utilisateurs
            flash("Si un compte est associé à cet identifiant, un e-mail de réinitialisation a été envoyé.", "info")

        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Vérifier le jeton (validité de 24 heures = 86400 secondes)
        email = s.loads(token, salt='password-reset-salt', max_age=86400)
    except:
        flash("Le lien de réinitialisation est invalide ou a expiré.", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template('reset_password.html', token=token)

        ldap_controller = ControleurLdap()
        user_dn = ldap_controller.get_user_dn_by_email(email)

        if user_dn:
            if ldap_controller.update_user_password(user_dn, password):
                flash("Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.", "success")
                return redirect(url_for('home_bp.home'))
            else:
                flash("Une erreur est survenue lors de la mise à jour du mot de passe.", "danger")
        else:
            flash("Utilisateur introuvable.", "danger")

        return redirect(url_for('forgot_password'))

    return render_template('reset_password.html', token=token)


# Enregistrer les routes
app.register_blueprint(home_bp)
app.register_blueprint(game_contents_bp)
app.register_blueprint(characters_bp)
app.register_blueprint(guides_bp)
app.register_blueprint(sjw_bp)
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    port = int(conf.get_config('APP', 'port'))
    app.run(debug=True, port=port)
