from static.Controleurs.ControleurLog import write_log

class CharactersSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_characters(self, language):
        write_log(f"Requête get_characters pour langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder, ct.character_translations_name
            FROM characters c
            JOIN character_translations ct ON ct.character_translations_characters_id = c.characters_id
            WHERE ct.character_translations_language = %s
        """, (language,))
        return self.cursor.fetchall()

    def get_character_details(self, language, alias):
        write_log(f"Requête get_character_details pour langue={language}, alias={alias}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder, ct.character_translations_name, ct.character_translations_description
            FROM characters c
            JOIN character_translations ct ON ct.character_translations_characters_id = c.characters_id
            WHERE ct.character_translations_language = %s AND c.characters_alias = %s
        """, (language, alias))
        return self.cursor.fetchone()

    # Ajoute ici toutes les autres méthodes CRUD et métiers pour characters