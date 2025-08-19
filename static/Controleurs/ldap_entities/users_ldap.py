from static.Controleurs.ControleurLdap import ControleurLdap
import ldap
from static.Controleurs.ControleurLog import write_log

class UsersLdap:
    def __init__(self, ds):
        self.ldap = ds

    def authenticate(self, username, password):
        try:
            self.ldap.bind_as_root()
            search_base = self.ldap.config.get_config('LDAP', 'base_dn')
            search_filter = f"(uid={username})"
            result = self.ldap.conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)

            if not result:
                write_log("Utilisateur non trouvé: " + username, 'ERROR')
                return False

            user_dn = result[0][0]
            self.ldap.conn.bind_s(user_dn, password)
            write_log("Authentification réussie de l'utilisateur: " + username)
            return True
        except ldap.INVALID_CREDENTIALS:
            write_log("Les informations d'identification sont incorrectes pour l'utilisateur: " + username, 'ERROR')
            return False
        except ldap.LDAPError as e:
            write_log("Erreur d'authentification pour l'utilisateur: " + username + " - " + str(e), 'ERROR')
            return False

    def search_user(self, username):
        try:
            self.ldap.bind_as_root()
            search_base = self.ldap.config.get_config('LDAP', 'base_dn')
            search_filter = f"(uid={username})"
            result = self.ldap.conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)
            if result:
                write_log("Utilisateur trouvé")
                return result
            else:
                write_log("Utilisateur non trouvé", 'ERROR')
                return None
        except ldap.LDAPError as e:
            write_log("Erreur lors de la recherche de l'utilisateur: " + str(e), 'ERROR')
            return None

    def add_user(self, dn, attributes):
        try:
            result = self.ldap.conn.add_s(dn, attributes)
            if result:
                write_log("Entrée " + dn + " ajoutée avec succès")
                return True
            else:
                write_log("Erreur lors de l'ajout de l'entrée: " + dn, 'ERROR')
                return None
        except ldap.LDAPError as e:
            write_log("Erreur lors de l'ajout de l'entrée: " + str(e), 'ERROR')

    def delete_user(self, username):
        try:
            self.ldap.bind_as_root()
            base_dn = self.ldap.config.get_config('LDAP', 'base_dn')
            dn = f'uid={username},{base_dn}'
            self.ldap.conn.delete_s(dn)
            write_log(f"Utilisateur {username} supprimé de la base LDAP")
            return True
        except ldap.LDAPError as e:
            write_log(f"Erreur lors de la suppression de l'utilisateur LDAP: {e}", 'ERROR')
            return False

    def add_attribute(self, username, attribute, value):
        try:
            self.ldap.bind_as_root()
            base_dn = self.ldap.config.get_config('LDAP', 'base_dn')
            dn = f'uid={username},dmdName=users,{base_dn}'
            mod_attrs = [(ldap.MOD_ADD, attribute, value.encode('utf-8'))]
            self.ldap.conn.modify_s(dn, mod_attrs)
            write_log(f"Attribut {attribute} ajouté pour l'utilisateur {username}")
            return True
        except ldap.LDAPError as e:
            write_log(f"Erreur lors de l'ajout de l'attribut LDAP: {e}", 'ERROR')
            return False

    def replace_attribute(self, username, attribute, value):
        try:
            self.ldap.bind_as_root()
            base_dn = self.ldap.config.get_config('LDAP', 'base_dn')
            dn = f'uid={username},dmdName=users,{base_dn}'
            mod_attrs = [(ldap.MOD_REPLACE, attribute, value.encode('utf-8'))]
            self.ldap.conn.modify_s(dn, mod_attrs)
            write_log(f"Attribut {attribute} remplacer pour l'utilisateur {username}")
            return True
        except ldap.LDAPError as e:
            write_log(f"Erreur lors du remplacement de l'attribut LDAP: {e}", 'ERROR')
            return False

    def get_all_users(self):
        try:
            self.ldap.bind_as_root()
            base_dn = self.ldap.config.get_config('LDAP', 'base_dn')
            search_filter = "(objectClass=inetOrgPerson)"
            result = self.ldap.conn.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)
            users = []
            for dn, entry in result:
                user = {attr: entry[attr][0].decode('utf-8') for attr in entry}
                users.append(user)
            write_log("Liste des utilisateurs récupérée")
            return users
        except ldap.LDAPError as e:
            write_log(f"Erreur lors de la récupération des utilisateurs LDAP: {e}", 'ERROR')
            return []

    def get_user_info(self, username):
        try:
            self.ldap.bind_as_root()
            base_dn = self.ldap.config.get_config('LDAP', 'base_dn')
            search_filter = f"(uid={username})"
            result = self.ldap.conn.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)
            if result:
                entry = result[0][1]
                write_log(f"Informations utilisateur récupérées pour {username}")
                return {attr: entry[attr] for attr in entry}
            else:
                write_log(f"Utilisateur {username} non trouvé dans get_user_info", 'WARNING')
                return {}
        except ldap.LDAPError as e:
            write_log(f"Erreur get_user_info pour {username}: {e}", 'ERROR')
            return {}

    def update_user(self, username, attributes):
        """
        Modifie les attributs d'un utilisateur LDAP.
        attributes : dict { 'attribut': 'valeur', ... }
        """
        try:
            self.ldap.bind_as_root()
            base_dn = self.ldap.config.get_config('LDAP', 'base_dn')
            dn = f'uid={username},dmdName=users,{base_dn}'
            mod_attrs = []
            for attr, value in attributes.items():
                mod_attrs.append((ldap.MOD_REPLACE, attr, value.encode('utf-8')))
            self.ldap.conn.modify_s(dn, mod_attrs)
            write_log(f"Utilisateur {username} modifié avec succès")
            return True
        except ldap.LDAPError as e:
            write_log(f"Erreur lors de la modification de l'utilisateur LDAP: {e}", 'ERROR')
            return False