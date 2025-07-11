from flask import request, jsonify, session
from static.Controleurs.ControleurLdap import ControleurLdap

ldap_ctrl = ControleurLdap()

def users(app):
    @app.route('/login', methods=['POST'])
    def login():
        username = request.form.get('username')
        password = request.form.get('password')
        if ldap_ctrl.authenticate_user(username, password):
            session['user'] = username
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Identifiants invalides'})

    @app.route('/register', methods=['POST'])
    def register():
        username = request.form.get('new_username')
        email = request.form.get('new_email')
        password = request.form.get('new_password')
        dn = f"uid={username},{ldap_ctrl.config.get_config('LDAP', 'base_dn')}"
        attrs = [
            ('objectClass', [b'inetOrgPerson']),
            ('uid', [username.encode('utf-8')]),
            ('mail', [email.encode('utf-8')]),
            ('userPassword', [password.encode('utf-8')])
        ]
        if ldap_ctrl.add_entry(dn, attrs):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Erreur lors de la création'})

    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return jsonify({'success': True})