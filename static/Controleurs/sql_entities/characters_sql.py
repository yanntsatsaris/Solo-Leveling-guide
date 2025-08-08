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

    def get_character_full(self, char_id, language):
        self.cursor.execute("""
            SELECT ct.character_translations_name, c.characters_alias, c.characters_type, c.characters_rarity, ct.character_translations_description
            FROM characters c
            JOIN character_translations ct ON ct.character_translations_characters_id = c.characters_id
            WHERE c.characters_id = %s AND ct.character_translations_language = %s
        """, (char_id, language))
        row = self.cursor.fetchone()
        if row:
            return {
                'name': row[0],
                'alias': row[1],
                'type': row[2],
                'rarity': row[3],
                'description': row[4]
            }
        return {}

    def update_character_main(self, char_id, alias, type_, rarity, image_name, name, description, language):
        self.cursor.execute("""
            UPDATE characters SET characters_alias=%s, characters_type=%s, characters_rarity=%s, characters_image=%s
            WHERE characters_id=%s
        """, (alias, type_, rarity, image_name, char_id))
        self.cursor.execute("""
            UPDATE character_translations SET character_translations_name=%s, character_translations_description=%s
            WHERE character_translations_characters_id=%s AND character_translations_language=%s
        """, (name, description, char_id, language))

    # Ajoute ici toutes les autres méthodes CRUD et métiers pour characters