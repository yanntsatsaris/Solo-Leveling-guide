from static.Controleurs.ControleurLog import write_log

class PassivesSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_passives(self, char_id, language):
        write_log(f"Requête get_passives pour char_id={char_id}, langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT p.passives_principal, pt.passive_translations_name, pt.passive_translations_description, p.passives_image
            FROM passives p
            JOIN passive_translations pt ON pt.passive_translations_passives_id = p.passives_id
            WHERE p.passives_characters_id = %s AND pt.passive_translations_language = %s
        """, (char_id, language))
        return self.cursor.fetchall()

    # Ajoute ici create, update, delete pour les passives