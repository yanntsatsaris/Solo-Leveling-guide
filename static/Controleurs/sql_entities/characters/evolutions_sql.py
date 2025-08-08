from static.Controleurs.ControleurLog import write_log

class EvolutionsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_evolutions(self, char_id, language, type_folder, char_folder):
        write_log(f"Requête get_evolutions pour char_id={char_id}, langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT ce.character_evolutions_id, ce.character_evolutions_evolution_id, ce.character_evolutions_number, ce.character_evolutions_type, ce.character_evolutions_range, cet.character_evolution_translations_description
            FROM character_evolutions ce
            LEFT JOIN character_evolution_translations cet ON cet.character_evolution_translations_character_evolutions_id = ce.character_evolutions_id
            WHERE ce.character_evolutions_characters_id = %s AND (cet.character_evolution_translations_language = %s OR cet.character_evolution_translations_language IS NULL)
        """, (char_id, language))
        return [
            {
                'id': row[0],  # Ajoute l'id
                'evolution_id': row[1],
                'number': row[2],
                'type': row[3],
                'range': row[4],
                'description': row[5] if row[5] else ''
            }
            for row in self.cursor.fetchall()
        ]

    def get_evolutions_full(self, char_id, language):
        self.cursor.execute("""
            SELECT ce.character_evolutions_id, ce.character_evolutions_evolution_id, ce.character_evolutions_number, cet.character_evolution_translations_description
            FROM character_evolutions ce
            LEFT JOIN character_evolution_translations cet ON cet.character_evolution_translations_character_evolutions_id = ce.character_evolutions_id
            WHERE ce.character_evolutions_characters_id = %s AND (cet.character_evolution_translations_language = %s OR cet.character_evolution_translations_language IS NULL)
        """, (char_id, language))
        return [
            {
                'id': row[0],
                'evolution_id': row[1],
                'number': row[2],
                'description': row[3] if row[3] else ''
            }
            for row in self.cursor.fetchall()
        ]

    def update_evolution(self, eid, char_id, evo_idx, evolution_id, desc, language):
        self.cursor.execute("""
            UPDATE character_evolution_translations SET character_evolution_translations_evolution_id=%s, character_evolution_translations_description=%s
            WHERE character_evolution_translations_character_evolutions_id=%s AND character_evolution_translations_language=%s
        """, (evolution_id, desc, eid, language))

    def add_evolution(self, char_id, evo_idx, evolution_id, desc, language):
        self.cursor.execute("""
            INSERT INTO character_evolutions (character_evolutions_characters_id, character_evolutions_number, character_evolutions_evolution_id)
            VALUES (%s, %s, %s) RETURNING character_evolutions_id
        """, (char_id, evo_idx, evolution_id))
        eid = self.cursor.fetchone()[0]
        self.cursor.execute("""
            INSERT INTO character_evolution_translations (character_evolution_translations_character_evolutions_id, character_evolution_translations_language, character_evolution_translations_description)
            VALUES (%s, %s, %s)
        """, (eid, language, desc))
        return eid