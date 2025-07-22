from flask import request, jsonify, session
from static.Controleurs.ControleurLdap import ControleurLdap
from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurLog import write_log
from passlib.hash import ldap_salted_sha1, ldap_sha1
import re

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
        username = request.form.get('username')
        password = request.form.get('password')
        if ldap.authenticate_user(username, password):
            # Vérification de l'attribut RightsAgreement
            user_info = ldap.get_user_info(username)
            rights = user_info.get('rightsAgreement', [])
            # Vérifie si l'attribut existe et contient "SoloLevelinGuide::"
            if not any(r.decode() if isinstance(r, bytes) else r for r in rights if "SoloLevelinGuide::" in (r.decode() if isinstance(r, bytes) else r)):
                write_log(f"Connexion refusée : pas de compte SoloLevelinGuide", log_level="WARNING", username=username)
                return jsonify({'success': False, 'error': "Aucun compte SoloLevelinGuide n'est associé à cet utilisateur."})
            session['user'] = username
            write_log(f"Connexion réussie", log_level="INFO", username=username)
            return jsonify({'success': True})
        write_log(f"Échec de connexion", log_level="WARNING", username=username)
        return jsonify({'success': False, 'error': 'Identifiants invalides'})

    @app.route('/register', methods=['POST'])
    def register():
        ldap = ControleurLdap()
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
            ('rightsAgreement', [b'SoloLevelinGuide::New']),  # Accord de droits par défaut
        ]
        if ldap.add_entry(dn, attrs):
            write_log(f"Création de compte réussie ({email})", log_level="INFO", username=username)
            return jsonify({'success': True})
        write_log(f"Échec de création de compte ({email})", log_level="ERROR", username=username)
        return jsonify({'success': False, 'error': 'Erreur lors de la création'})

    @app.route('/logout')
    def logout():
        username = session.pop('user', None)
        write_log("Déconnexion", log_level="INFO", username=username)
        return jsonify({'success': True})