from collections import Counter
from static.Controleurs.ControleurLog import write_log

class EquipmentSetSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_equipment_sets(self, char_id, language):
        write_log(f"Requête get_equipment_sets pour char_id={char_id}, langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT es.equipment_sets_id, es.equipment_sets_name
            FROM equipment_sets es
            WHERE es.equipment_sets_characters_id = %s
        """, (char_id,))
        return self.cursor.fetchall()

    def get_equipment_set_details(self, eq_set_id, eq_set_name, language):
        write_log(f"Requête get_equipment_set_details pour eq_set_id={eq_set_id}, eq_set_name={eq_set_name}, langue={language}", log_level="DEBUG")
        # Description traduite du set
        self.cursor.execute("""
            SELECT equipment_set_translations_description
            FROM equipment_set_translations
            WHERE equipment_set_translations_equipment_sets_id = %s AND equipment_set_translations_language = %s
        """, (eq_set_id, language))
        desc_row = self.cursor.fetchone()
        set_description = desc_row[0] if desc_row else ""
        # Focus stats
        self.cursor.execute("""
            SELECT equipment_focus_stats_name FROM equipment_focus_stats
            WHERE equipment_focus_stats_equipment_sets_id = %s
        """, (eq_set_id,))
        focus_stats = [fs_row[0] for fs_row in self.cursor.fetchall()]
        # Artefacts
        self.cursor.execute("""
            SELECT a.artefacts_id, at.artefact_translations_name, at.artefact_translations_set, a.artefacts_image, a.artefacts_main_stat
            FROM artefacts a
            JOIN artefact_translations at ON at.artefact_translations_artefacts_id = a.artefacts_id
            WHERE a.artefacts_equipment_sets_id = %s AND at.artefact_translations_language = %s
        """, (eq_set_id, language))
        artefacts = []
        artefact_sets = []
        for a_row in self.cursor.fetchall():
            artefact_id, artefact_name, artefact_set, artefact_image, artefact_main_stat = a_row
            self.cursor.execute("""
                SELECT artefact_secondary_stats_name FROM artefact_secondary_stats
                WHERE artefact_secondary_stats_artefacts_id = %s
            """, (artefact_id,))
            secondary_stats = [sec_row[0] for sec_row in self.cursor.fetchall()]
            artefact_obj = {
                'name': artefact_name,
                'set': artefact_set,
                'image': f'images/Artefacts/{artefact_image}' if artefact_image else '',
                'iamage_name': artefact_image,
                'main_stat': artefact_main_stat,
                'secondary_stats': secondary_stats
            }
            artefacts.append(artefact_obj)
            artefact_sets.append(artefact_set)
        # Noyaux
        self.cursor.execute("""
            SELECT cores_name, cores_number, cores_image, cores_main_stat, cores_secondary_stat
            FROM cores
            WHERE cores_equipment_sets_id = %s
        """, (eq_set_id,))
        cores = []
        for core_row in self.cursor.fetchall():
            core_obj = {
                'name': core_row[0],
                'number': core_row[1],
                'image': f'images/Noyaux/{core_row[2]}' if core_row[2] else '',
                'image_name': core_row[2],
                'main_stat': core_row[3],
                'secondary_stat': core_row[4]
            }
            cores.append(core_obj)
        set_piece_count = Counter(artefact_sets)
        return {
            'set_name': eq_set_name,
            'description': set_description,  # Ajout de la description traduite
            'focus_stats': focus_stats,
            'artefacts': artefacts,
            'cores': cores,
            'set_piece_count': dict(set_piece_count)
        }