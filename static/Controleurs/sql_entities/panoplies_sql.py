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