from static.Controleurs.ControleurLog import write_log

class EvolutionsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_evolutions(self, char_id, language, type_folder, char_folder):
        write_log(f"Requête get_evolutions pour char_id={char_id}, langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT ce.character_evolutions_evolution_id, ce.character_evolutions_number, ce.character_evolutions_type, ce.character_evolutions_range, cet.character_evolution_translations_description
            FROM character_evolutions ce
            LEFT JOIN character_evolution_translations cet ON cet.character_evolution_translations_character_evolutions_id = ce.character_evolutions_id
            WHERE ce.character_evolutions_characters_id = %s AND (cet.character_evolution_translations_language = %s OR cet.character_evolution_translations_language IS NULL)
        """, (char_id, language))
        return [
            {
                'id': row[0],
                'number': row[1],
                'type': row[2],
                'range': row[3],
                'description': row[4] if row[4] else ''
            }
            for row in self.cursor.fetchall()
        ]