from flask import request, jsonify, session
from static.Controleurs.ControleurLdap import ControleurLdap
from static.Controleurs.ControleurLog import write_log


def users(app):
    @app.route('/login', methods=['POST'])
    def login():
        ldap = ControleurLdap()
        username = request.form.get('username')
        password = request.form.get('password')
        if ldap.authenticate_user(username, password):
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
        dn = f"uid={username},{ldap.config.get_config('LDAP', 'base_dn')}"
        attrs = [
            ('objectClass', [b'inetOrgPerson']),
            ('uid', [username.encode('utf-8')]),
            ('mail', [email.encode('utf-8')]),
            ('userPassword', [password.encode('utf-8')])
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