from static.Controleurs.ControleurLog import write_log

class CoresSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_cores_effects(self, language):
        write_log(f"Requête get_all_core_effects pour langue={language}", log_level="DEBUG")
        query = """
            SELECT ce.cores_effects_color, ce.cores_effects_number, cet.core_effect_translations_name, cet.core_effect_translations_effect
            FROM cores_effects ce
            JOIN core_effect_translations cet ON cet.core_effect_translations_cores_effects_id = ce.cores_effects_id
            WHERE cet.core_effect_translations_language = %s
        """
        self.cursor.execute(query, (language,))
        return [
            {
                'color': row[0],
                'number': row[1],
                'name': row[2],
                'effect': row[3]
            }
            for row in self.cursor.fetchall()
        ]

    def get_all_cores(self, language='FR-fr'):
        write_log(f"Requête get_all_cores pour langue={language}", log_level="DEBUG")
        query = """
            SELECT ce.cores_effects_id, ce.cores_effects_color, ce.cores_effects_number,
                   cet.core_effect_translations_name, cet.core_effect_translations_effect
            FROM cores_effects ce
            LEFT JOIN core_effect_translations cet
                ON cet.core_effect_translations_cores_effects_id = ce.cores_effects_id
                AND cet.core_effect_translations_language = %s
            ORDER BY ce.cores_effects_color, ce.cores_effects_number
        """
        self.cursor.execute(query, (language,))
        return [
            {
                'id': row[0],
                'color': row[1],
                'number': row[2],
                'effect_name': row[3],
                'effect': row[4]
            }
            for row in self.cursor.fetchall()
        ]