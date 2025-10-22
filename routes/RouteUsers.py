from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, abort, current_app
from itsdangerous import URLSafeTimedSerializer
from static.Controleurs.ControleurMail import send_email
from static.Controleurs.ControleurLdap import ControleurLdap
from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurLog import write_log
from passlib.hash import ldap_salted_sha1, ldap_sha1
import re
from static.Controleurs.ControleurUser import User
from flask_login import login_user, login_required, logout_user

# Import des entités ldap segmentées
from static.Controleurs.ldap_entities.users_ldap import UsersLdap
from static.Controleurs.ldap_entities.entries_ldap import EntriesLdap

users_bp = Blueprint('users', __name__)

def is_hashed(password):
    # Vérifie si le mot de passe est déjà haché avec SHA, SSHA, MD5, CRYPT ou SMD5
    hash_patterns = [
        r'^\{SHA\}', r'^\{SSHA\}', r'^\{MD5\}', r'^\{CRYPT\}', r'^\{SMD5\}'
    ]
    return any(re.match(pattern, password) for pattern in hash_patterns)

def get_reset_token(username, salt='password-reset-salt'):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(username, salt=salt)

def verify_reset_token(token, salt='password-reset-salt', max_age=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        username = serializer.loads(token, salt=salt, max_age=max_age)
    except:
        return None
    return username

@users_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        ldap = ControleurLdap()

        # Déterminer si l'identifiant est un email ou un username
        if '@' in identifier:
            # Recherche par email
            # NOTE: Cette fonctionnalité dépend de la capacité à rechercher par email dans LDAP
            # Ce qui n'est pas implémenté dans ControleurLdap.py. On se concentre sur l'username.
            # Pour une future amélioration, il faudrait ajouter une méthode search_by_email.
            return render_template('forgot_password.html', error="La recherche par e-mail n'est pas encore supportée.")
        else:
            # Recherche par nom d'utilisateur
            user_info = ldap.get_user_info(identifier)
            if user_info:
                username = user_info['uid'][0].decode()
                email = user_info['mail'][0].decode()
                token = get_reset_token(username)
                reset_url = url_for('users.reset_password', token=token, _external=True)
                send_email(
                    to=email,
                    subject='Réinitialisation de votre mot de passe',
                    template='emails/reset_password.html',
                    username=username,
                    reset_url=reset_url
                )
                return render_template('forgot_password.html', message="Un e-mail de réinitialisation a été envoyé.")
            else:
                return render_template('forgot_password.html', error="Utilisateur non trouvé.")

    return render_template('forgot_password.html')

@users_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    username = verify_reset_token(token)
    if not username:
        return 'Le lien de réinitialisation est invalide ou a expiré.', 400

    if request.method == 'POST':
        new_password = request.form.get('password')
        hashed_password = ldap_salted_sha1.hash(new_password)

        ldap = ControleurLdap()
        users_ldap = UsersLdap(ldap)
        if users_ldap.update_user(username, {'userPassword': hashed_password}):
            # Idéalement, informer l'utilisateur sur la page de connexion
            return redirect(url_for('users.login'))
        else:
            return 'Erreur lors de la mise à jour du mot de passe.', 500

    return render_template('reset_password.html', token=token)

@users_bp.route('/login', methods=['POST'])
def login():
    ldap = ControleurLdap()
    users_ldap = UsersLdap(ldap)
    username = request.form.get('username')
    password = request.form.get('password')
    if users_ldap.authenticate(username, password):
        user_info = ldap.get_user_info(username)
        rights = user_info.get('rightsAgreement', [])
        solo_rights = [r.decode() if isinstance(r, bytes) else r for r in rights if "SoloLevelingGuide::" in (r.decode() if isinstance(r, bytes) else r)]
        if not solo_rights:
            write_log(f"Connexion refusée : pas de compte SoloLevelingGuide", log_level="WARNING", username=username)
            return jsonify({'success': False, 'error': "Aucun compte SoloLevelingGuide n'est associé à cet utilisateur."})
        rights = [r.split("SoloLevelingGuide::")[1] for r in solo_rights]
        session['username'] = username
        session['rights'] = rights
        user = User(username, rights)
        login_user(user)
        write_log(f"Connexion réussie", log_level="INFO", username=username)
        write_log(f"Niveau SoloLevelingGuide de {username}: {', '.join(rights)}", log_level="INFO", username=username)
        return jsonify({'success': True})
    write_log(f"Échec de connexion", log_level="WARNING", username=username)
    return jsonify({'success': False, 'error': 'Identifiants invalides'})

@users_bp.route('/register', methods=['POST'])
def register():
    ldap = ControleurLdap()
    users_ldap = UsersLdap(ldap)
    username = request.form.get('new_username')
    email = request.form.get('new_email')
    password = request.form.get('new_password')

    if not is_hashed(password):
        hashed_password = ldap_salted_sha1.hash(password)
    else:
        hashed_password = password
    conf = ControleurConf()
    base_dn = conf.get_config('LDAP', 'base_dn')
    if ldap.search_user(username):
        write_log(f"L'utilisateur {username} existe déjà")
        ldap.disconnect()
        return jsonify({'success': False, 'error': 'Utilisateur déjà existant'}), 409
    write_log(f"L'utilisateur {username} n'existe pas, ajout en cours")
    dn = f"uid={username},dmdName=users,{base_dn}"
    attrs = [
        ('objectClass', [b'inetOrgPerson', b'organizationalPerson', b'person', b'otherUserInfos']),
        ('uid', [username.encode('utf-8')]),
        ('sn', [username.encode('utf-8')]),
        ('cn', [username.encode('utf-8')]),
        ('mail', [email.encode('utf-8')]),
        ('userPassword', [hashed_password.encode('utf-8')]),
        ('rightsAgreement', [b'SoloLevelingGuide::New']),
    ]
    if users_ldap.add_user(dn, attrs):
        write_log(f"Création de compte réussie ({username})", log_level="INFO", username=username)
        return jsonify({'success': True})
    write_log(f"Échec de création de compte ({username})", log_level="ERROR", username=username)
    return jsonify({'success': False, 'error': 'Erreur lors de la création'})

@users_bp.route('/logout')
def logout():
    username = session.pop('username', None)
    logout_user()
    write_log("Déconnexion", log_level="INFO", username=username)
    return jsonify({'success': True})

@users_bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_profile(username):
    write_log(f"Accès au profil de {username}", log_level="INFO", username=username)
    RIGHTS_ORDER = ['New', 'User', 'Admin', 'SuperAdmin']

    ldap = ControleurLdap()
    users_ldap = UsersLdap(ldap)
    user_info = users_ldap.get_user_info(username)
    if not user_info:
        abort(404)

    target_rights = user_info.get('rightsAgreement', [])
    target_rights = [r.decode() if isinstance(r, bytes) else r for r in target_rights]
    target_rights = [r.split("SoloLevelingGuide::")[1] for r in target_rights if "SoloLevelingGuide::" in (r.decode() if isinstance(r, bytes) else r)]
    target_max = max((RIGHTS_ORDER.index(r) for r in target_rights if r in RIGHTS_ORDER), default=0)

    my_rights = session.get('rights', [])
    my_max = max((RIGHTS_ORDER.index(r) for r in my_rights if r in RIGHTS_ORDER), default=0)

    if session.get('username') != username:
        if my_max < RIGHTS_ORDER.index('Admin') or not (my_max > target_max):
            abort(403)

    if request.method == 'POST':
        new_email = request.form.get('email')
        new_password = request.form.get('password')
        attributes = {}
        if new_email:
            attributes['mail'] = new_email
        if new_password:
            if not is_hashed(new_password):
                new_hashed_password = ldap_salted_sha1.hash(new_password)
            else:
                new_hashed_password = new_password
            attributes['userPassword'] = new_hashed_password

        if attributes:
            users_ldap.update_user(username, attributes)
            write_log(f"Modification du compte {username}", log_level="INFO", username=username)
        return redirect(url_for('users.user_profile', username=username))

    is_admin = my_max >= RIGHTS_ORDER.index('Admin')
    return render_template('user_profile.html', user=user_info, is_admin=is_admin)
