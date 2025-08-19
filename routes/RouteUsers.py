from flask import request, jsonify, session, render_template, redirect, url_for, abort
from static.Controleurs.ControleurLdap import ControleurLdap
from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurLog import write_log
from passlib.hash import ldap_salted_sha1, ldap_sha1
import re
from static.Controleurs.ControleurUser import User
from flask_login import login_user, login_required

# Import des entités ldap segmentées
from static.Controleurs.ldap_entities.users_ldap import UsersLdap
from static.Controleurs.ldap_entities.entries_ldap import EntriesLdap


def is_hashed(password):
    # Vérifie si le mot de passe est déjà haché avec SHA, SSHA, MD5, CRYPT ou SMD5
    hash_patterns = [
        r'^\{SHA\}', r'^\{SSHA\}', r'^\{MD5\}', r'^\{CRYPT\}', r'^\{SMD5\}'
    ]
    return any(re.match(pattern, password) for pattern in hash_patterns)

def users(app):
    @app.route('/login', methods=['POST'])
    def login():
        ldap = ControleurLdap()
        users_ldap = UsersLdap(ldap)
        username = request.form.get('username')
        password = request.form.get('password')
        if users_ldap.authenticate(username, password):
            # Vérification de l'attribut RightsAgreement
            user_info = ldap.get_user_info(username)
            rights = user_info.get('rightsAgreement', [])
            # Vérifie si l'attribut existe et contient "SoloLevelingGuide::"
            solo_rights = [r.decode() if isinstance(r, bytes) else r for r in rights if "SoloLevelingGuide::" in (r.decode() if isinstance(r, bytes) else r)]
            if not solo_rights:
                write_log(f"Connexion refusée : pas de compte SoloLevelingGuide", log_level="WARNING", username=username)
                return jsonify({'success': False, 'error': "Aucun compte SoloLevelingGuide n'est associé à cet utilisateur."})
            rights = [r.split("SoloLevelingGuide::")[1] for r in solo_rights]  # Stocke le niveau dans rights
            session['username'] = username
            session['rights'] = rights  # Stocke dans la session
            user = User(username, rights)
            login_user(user)
            write_log(f"Connexion réussie", log_level="INFO", username=username)
            write_log(f"Niveau SoloLevelingGuide de {username}: {', '.join(rights)}", log_level="INFO", username=username)
            return jsonify({'success': True})
        write_log(f"Échec de connexion", log_level="WARNING", username=username)
        return jsonify({'success': False, 'error': 'Identifiants invalides'})

    @app.route('/register', methods=['POST'])
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
        # Vérifier si le compte existe déjà
        if ldap.search_user(username):
            write_log(f"L'utilisateur {username} existe déjà")
            ldap.disconnect()
            return jsonify({'success': False, 'error': 'Utilisateur déjà existant'}), 409
        write_log(f"L'utilisateur {username} n'existe pas, ajout en cours")
        dn = f"uid={username},dmdName=users,{base_dn}"
        attrs = [
            ('objectClass', [b'inetOrgPerson', b'organizationalPerson', b'person', b'otherUserInfos']),
            ('uid', [username.encode('utf-8')]),
            ('sn', [username.encode('utf-8')]),  # Nom de famille
            ('cn', [username.encode('utf-8')]),  # Nom complet
            ('mail', [email.encode('utf-8')]),
            ('userPassword', [hashed_password.encode('utf-8')]),
            ('rightsAgreement', [b'SoloLevelingGuide::New']),  # Accord de droits par défaut
        ]
        if users_ldap.add_user(dn, attrs):
            write_log(f"Création de compte réussie ({username})", log_level="INFO", username=username)
            return jsonify({'success': True})
        write_log(f"Échec de création de compte ({username})", log_level="ERROR", username=username)
        return jsonify({'success': False, 'error': 'Erreur lors de la création'})

    @app.route('/logout')
    def logout():
        username = session.pop('username', None)
        write_log("Déconnexion", log_level="INFO", username=username)
        return jsonify({'success': True})

    @app.route('/user/<username>', methods=['GET', 'POST'])
    @login_required
    def user_profile(username):
        write_log(f"Accès au profil de {username}", log_level="INFO", username=username)
        # Vérifie que l'utilisateur connecté correspond à la page demandée ou qu'il est admin
        if session.get('username') != username and not (
            session.get('rights') and ('Admin' in session['rights'] or 'SuperAdmin' in session['rights'])
        ):
            abort(403)

        ldap = ControleurLdap()
        users_ldap = UsersLdap(ldap)
        # Récupère les infos utilisateur depuis la BDD (à adapter selon ta structure)
        user_info = users_ldap.get_user_info(username)

        if request.method == 'POST':
            # Récupère les champs à modifier
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
            # Ajoute d'autres champs si besoin

            if attributes:
                users_ldap.update_user(username, attributes)
                write_log(f"Modification du compte {username}", log_level="INFO", username=username)
            return redirect(url_for('user_profile', username=username))

        is_admin = session.get('rights') and ('Admin' in session['rights'] or 'SuperAdmin' in session['rights'])
        return render_template('user_profile.html', user=user_info, is_admin=is_admin)