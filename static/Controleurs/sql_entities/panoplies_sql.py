from static.Controleurs.ControleurLog import write_log

class PanopliesSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_panoplies(self, language):
        write_log(f"Requête get_panoplies pour langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT p.panoplies_name, pt.panoplie_translations_name, pt.panoplie_translations_display_name, pt.panoplie_translations_language
            FROM panoplies p
            JOIN panoplie_translations pt ON pt.panoplie_translations_panoplies_id = p.panoplies_id
            WHERE pt.panoplie_translations_language = %s
        """, (language,))
        return self.cursor.fetchall()

    def get_panoplies_effects(self, language):
        write_log(f"Requête get_panoplies_effects pour langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT p.panoplies_name, pt.panoplie_translations_display_name, psb.panoplie_set_bonus_pieces_required, psbt.panoplie_set_bonus_translations_effect
            FROM panoplies p
            JOIN panoplie_translations pt ON pt.panoplie_translations_panoplies_id = p.panoplies_id
            JOIN panoplie_set_bonus psb ON psb.panoplie_set_bonus_panoplies_id = p.panoplies_id
            JOIN panoplie_set_bonus_translations psbt ON psbt.panoplie_set_bonus_translations_panoplie_set_bonus_id = psb.panoplie_set_bonus_id
            WHERE pt.panoplie_translations_language = %s AND psbt.panoplie_set_bonus_translations_language = %s
        """, (language, language))
        return [
            {
                'set_name': row[0],
                'display_name': row[1],
                'pieces_required': row[2],
                'effect': row[3]
            }
            for row in self.cursor.fetchall()
        ]

    def get_panoplie_by_name(self, panoplie_name, language):
        self.cursor.execute("""
            SELECT p.panoplies_name, pt.panoplie_translations_display_name
            FROM panoplies p
            JOIN panoplie_translations pt ON pt.panoplie_translations_panoplies_id = p.panoplies_id
            WHERE p.panoplies_name = %s AND pt.panoplie_translations_language = %s
        """, (panoplie_name, language))
        return self.cursor.fetchone()

    def get_panoplie_effects(self, panoplie_name, language):
        self.cursor.execute("""
            SELECT psb.panoplie_set_bonus_pieces_required, psbt.panoplie_set_bonus_translations_effect
            FROM panoplies p
            JOIN panoplie_set_bonus psb ON psb.panoplie_set_bonus_panoplies_id = p.panoplies_id
            JOIN panoplie_set_bonus_translations psbt ON psbt.panoplie_set_bonus_translations_panoplie_set_bonus_id = psb.panoplie_set_bonus_id
            WHERE p.panoplies_name = %s AND psbt.panoplie_set_bonus_translations_language = %s
        """, (panoplie_name, language))
        return self.cursor.fetchall()

    def update_panoplie_display_name(self, panoplie_name, language, new_display_name):
        write_log(
            f"Modification du nom affiché de la panoplie '{panoplie_name}' pour la langue '{language}' : '{new_display_name}'",
            log_level="INFO"
        )
        self.cursor.execute("""
            UPDATE panoplie_translations
            SET panoplie_translations_display_name = %s
            WHERE panoplies_id = (SELECT panoplies_id FROM panoplies WHERE panoplies_name = %s)
            AND panoplie_translations_language = %s
        """, (new_display_name, panoplie_name, language))

    def update_panoplie_effect(self, panoplie_name, language, pieces, effect):
        write_log(
            f"Modification de l'effet ({pieces} pièces) de la panoplie '{panoplie_name}' pour la langue '{language}' : '{effect}'",
            log_level="INFO"
        )
        self.cursor.execute("""
            UPDATE panoplie_set_bonus_translations
            SET panoplie_set_bonus_translations_effect = %s
            WHERE panoplie_set_bonus_translations_panoplie_set_bonus_id = (
                SELECT psb.panoplie_set_bonus_id
                FROM panoplies p
                JOIN panoplie_set_bonus psb ON psb.panoplie_set_bonus_panoplies_id = p.panoplies_id
                WHERE p.panoplies_name = %s AND psb.panoplie_set_bonus_pieces_required = %s
            )
            AND panoplie_set_bonus_translations_language = %s
        """, (effect, panoplie_name, pieces, language))

    def get_panoplie_all_languages(self, panoplie_name):
        self.cursor.execute("""
            SELECT pt.panoplie_translations_language, pt.panoplie_translations_display_name
            FROM panoplies p
            JOIN panoplie_translations pt ON pt.panoplie_translations_panoplies_id = p.panoplies_id
            WHERE p.panoplies_name = %s
        """, (panoplie_name,))
        translations = {row[0]: {'display_name': row[1]} for row in self.cursor.fetchall()}

        self.cursor.execute("""
            SELECT psbt.panoplie_set_bonus_translations_language, psb.panoplie_set_bonus_pieces_required, psbt.panoplie_set_bonus_translations_effect
            FROM panoplies p
            JOIN panoplie_set_bonus psb ON psb.panoplie_set_bonus_panoplies_id = p.panoplies_id
            JOIN panoplie_set_bonus_translations psbt ON psbt.panoplie_set_bonus_translations_panoplie_set_bonus_id = psb.panoplie_set_bonus_id
            WHERE p.panoplies_name = %s
        """, (panoplie_name,))
        effects = {}
        for lang, pieces, effect in self.cursor.fetchall():
            effects.setdefault(lang, []).append({'pieces': pieces, 'effect': effect})

        return {'translations': translations, 'effects': effects}