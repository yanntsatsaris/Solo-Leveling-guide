from static.Controleurs.ControleurLog import write_log

class CharactersSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_characters(self):
        write_log(f"Requête get_characters", log_level="DEBUG")
        self.cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder, ct.character_translations_name
            FROM characters c
        """)
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

    def update_character_main(self, char_id, alias, type_, rarity, name, description, language):
        self.cursor.execute("""
            UPDATE characters SET characters_alias=%s, characters_type=%s, characters_rarity=%s
            WHERE characters_id=%s
        """, (alias, type_, rarity, char_id))
        self.cursor.execute("""
            UPDATE character_translations SET character_translations_name=%s, character_translations_description=%s
            WHERE character_translations_characters_id=%s AND character_translations_language=%s
        """, (name, description, char_id, language))

    def add_character(self, alias, type_, rarity, name, description, folder, language):
        # Vérifie si un personnage avec cet alias existe déjà
        self.cursor.execute("""
            SELECT characters_id FROM characters WHERE characters_alias = %s
        """, (alias,))
        row = self.cursor.fetchone()
        if row:
            # Retourne l'id existant si déjà présent
            return row[0]

        # Ajoute le personnage principal
        self.cursor.execute("""
            INSERT INTO characters (characters_alias, characters_type, characters_rarity, characters_folder)
            VALUES (%s, %s, %s, %s) RETURNING characters_id
        """, (alias, type_, rarity, folder))
        char_id = self.cursor.fetchone()[0]

        # Ajoute la traduction principale
        self.cursor.execute("""
            INSERT INTO character_translations (character_translations_characters_id, character_translations_language, character_translations_name, character_translations_description)
            VALUES (%s, %s, %s, %s)
        """, (char_id, language, name, description))

        return char_id

    # Ajoute ici toutes les autres méthodes CRUD et métiers pour characters