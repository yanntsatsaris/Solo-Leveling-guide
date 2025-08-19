from static.Controleurs.ControleurLdap import ControleurLdap
import ldap
from static.Controleurs.ControleurLog import write_log

class EntriesLdap:
    def __init__(self, ds):
        self.ldap = ds

    def add_entry(self, dn, attributes):
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

    def delete_entry(self, dn):
        try:
            self.ldap.bind_as_root()
            self.ldap.conn.delete_s(dn)
            write_log("Entrée supprimée avec succès")
            return True
        except ldap.LDAPError as e:
            write_log("Erreur lors de la suppression de l'entrée: " + str(e), 'ERROR')
            return False

    def modify_entry(self, dn, mod_list):
        try:
            self.ldap.bind_as_root()
            write_log(f"Modification de l'entrée {dn} avec les attributs {mod_list}")
            self.ldap.conn.modify_s(dn, mod_list)
            write_log("Entrée modifiée avec succès")
            return True
        except ldap.LDAPError as e:
            write_log("Erreur lors de la modification de l'entrée: " + str(e), 'ERROR')
            return False

    def search_entry(self, search_base, search_filter):
        try:
            self.ldap.bind_as_root()
            result = self.ldap.conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)
            if result:
                write_log("Entrée trouvée")
                return result
            else:
                write_log("Entrée non trouvée", 'ERROR')
                return None
        except ldap.LDAPError as e:
            write_log("Erreur lors de la recherche de l'entrée: " + str(e), 'ERROR')

    def validate_wish(self, dn):
        try:
            self.ldap.bind_as_root()
            mod_attrs = [(ldap.MOD_REPLACE, 'status', b'validated')]
            self.ldap.conn.modify_s(dn, mod_attrs)
            write_log(f"Demande validée pour l'entrée {dn}")
            return True
        except ldap.LDAPError as e:
            write_log(f"Erreur lors de la validation de la demande: {e}", 'ERROR')
            return False
