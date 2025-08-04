from static.Controleurs.ControleurLog import write_log

class PassivesSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_passives(self, char_id, language, type_folder, char_folder):
        write_log(f"Requête get_passives pour char_id={char_id}, langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT p.passives_principal, pt.passive_translations_name, pt.passive_translations_description, p.passives_image, pt.passive_translations_tag, p.passives_hidden
            FROM passives p
            JOIN passive_translations pt ON pt.passive_translations_passives_id = p.passives_id
            WHERE p.passives_characters_id = %s AND pt.passive_translations_language = %s
        """, (char_id, language))
        return [
            {
                'principal': row[0],
                'name': row[1],
                'description': row[2],
                'image': f'images/Personnages/{type_folder}/{char_folder}/{row[3]}' if row[3] else '',
                'tag': row[4],
                'hidden': row[5]  # Ajout du champ hidden
            }
            for row in self.cursor.fetchall()
        ]

    # Ajoute ici create, update, delete pour les passives