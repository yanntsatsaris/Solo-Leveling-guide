from static.Controleurs.ControleurLog import write_log

class CharactersSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_characters(self, language):
        write_log(f"Requête get_characters (ordre rareté/type/nom, traduction {language})", log_level="DEBUG")
        self.cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder,
                   ct.character_translations_name
            FROM characters c
            LEFT JOIN character_translations ct
              ON ct.character_translations_characters_id = c.characters_id
             AND ct.character_translations_language = %s
            ORDER BY
                CASE c.characters_rarity
                    WHEN 'SSR' THEN 1
                    WHEN 'SR' THEN 2
                    ELSE 3
                END,
                c.characters_type,
                ct.character_translations_name
        """, (language,))
        return self.cursor.fetchall()

    def get_character_details(self, language, alias):
        write_log(f"Requête get_character_details pour langue={language}, alias={alias}", log_level="DEBUG")
        # Récupère les infos principales du personnage
        self.cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder
            FROM characters c
            WHERE c.characters_alias = %s
        """, (alias,))
        char_row = self.cursor.fetchone()
        if not char_row:
            return None

        char_id, type_, rarity, alias, folder = char_row

        # Récupère la traduction pour la langue demandée
        self.cursor.execute("""
            SELECT character_translations_name, character_translations_description
            FROM character_translations
            WHERE character_translations_characters_id = %s AND character_translations_language = %s
        """, (char_id, language))
        trans_row = self.cursor.fetchone()
        if trans_row:
            name, description = trans_row
        else:
            name, description = '', ''

        return {
            'characters_id': char_id,
            'characters_type': type_,
            'characters_rarity': rarity,
            'characters_alias': alias,
            'characters_folder': folder,
            'character_translations_name': name,
            'character_translations_description': description
        }

    def get_character_full(self, char_id, language):
        self.cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder
            FROM characters c
            WHERE c.characters_id = %s
        """, (char_id,))
        char_row = self.cursor.fetchone()
        if not char_row:
            return None

        char_id, type_, rarity, alias, folder = char_row

        # Récupère la traduction pour la langue demandée
        self.cursor.execute("""
            SELECT character_translations_name, character_translations_description
            FROM character_translations
            WHERE character_translations_characters_id = %s AND character_translations_language = %s
        """, (char_id, language))
        trans_row = self.cursor.fetchone()
        if trans_row:
            name, description = trans_row
        else:
            name, description = '', ''
 
        return {
            'name': name or '',
            'alias': alias or '',
            'type': type_ or '',
            'rarity': rarity or '',
            'description': description or ''
        }

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
            char_id = row[0]
            # Vérifie si une traduction existe déjà pour cette langue
            self.cursor.execute("""
                SELECT 1 FROM character_translations
                WHERE character_translations_characters_id = %s AND character_translations_language = %s
            """, (char_id, language))
            if not self.cursor.fetchone():
                # Ajoute la traduction manquante
                self.cursor.execute("""
                    INSERT INTO character_translations (character_translations_characters_id, character_translations_language, character_translations_name, character_translations_description)
                    VALUES (%s, %s, %s, %s)
                """, (char_id, language, name, description))
            return char_id

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