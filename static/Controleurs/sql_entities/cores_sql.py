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

    def get_core_effect(self, color, number, language):
        self.cursor.execute("""
            SELECT cet.core_effect_translations_name, cet.core_effect_translations_effect
            FROM cores_effects ce
            LEFT JOIN core_effect_translations cet
                ON cet.core_effect_translations_cores_effects_id = ce.cores_effects_id
                AND cet.core_effect_translations_language = %s
            WHERE ce.cores_effects_color = %s AND ce.cores_effects_number = %s
        """, (language, color, number))
        row = self.cursor.fetchone()
        return {
            "name": row[0] if row else "",
            "effect": row[1] if row else ""
        }

    def update_core_effect_name(self, color, number, language, new_name):
        write_log(
            f"Modification du nom du core '{color}{number}' pour la langue '{language}' : '{new_name}'",
            log_level="INFO"
        )
        self.cursor.execute("""
            UPDATE core_effect_translations cet
            SET core_effect_translations_name = %s
            FROM cores_effects ce
            WHERE cet.core_effect_translations_cores_effects_id = ce.cores_effects_id
              AND ce.cores_effects_color = %s
              AND ce.cores_effects_number = %s
              AND cet.core_effect_translations_language = %s
        """, (new_name, color, number, language))

    def update_core_effect(self, color, number, language, new_effect):
        write_log(
            f"Modification de l'effet du core '{color}{number}' pour la langue '{language}' : '{new_effect}'",
            log_level="INFO"
        )
        self.cursor.execute("""
            UPDATE core_effect_translations cet
            SET core_effect_translations_effect = %s
            FROM cores_effects ce
            WHERE cet.core_effect_translations_cores_effects_id = ce.cores_effects_id
              AND ce.cores_effects_color = %s
              AND ce.cores_effects_number = %s
              AND cet.core_effect_translations_language = %s
        """, (new_effect, color, number, language))

    def core_exists(self, color, number):
        self.cursor.execute("SELECT 1 FROM cores_effects WHERE cores_effects_color = %s AND cores_effects_number = %s", (color, number))
        return self.cursor.fetchone() is not None

    def create_core(self, color, number):
        self.cursor.execute(
            "INSERT INTO cores_effects (cores_effects_color, cores_effects_number) VALUES (%s, %s) RETURNING cores_effects_id",
            (color, number)
        )
        return self.cursor.fetchone()[0]

    def create_core_translation(self, core_id, lang, name, effect):
        self.cursor.execute(
            "INSERT INTO core_effect_translations (core_effect_translations_cores_effects_id, core_effect_translations_language, core_effect_translations_name, core_effect_translations_effect) VALUES (%s, %s, %s, %s)",
            (core_id, lang, name, effect)
        )