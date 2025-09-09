class SJWEquipmentSetSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_equipment_sets_full(self, sjw_id, language):
        self.cursor.execute("""
            SELECT es.sjw_equipment_sets_id, es.sjw_equipment_sets_name
            FROM sjw_equipment_sets es
            WHERE es.sjw_equipment_sets_sjw_id = %s
            ORDER BY es.sjw_equipment_sets_id ASC
        """, (sjw_id,))
        sets = []
        for row in self.cursor.fetchall():
            set_id, set_name = row
            # Description traduite du set
            self.cursor.execute("""
                SELECT sjw_equipment_set_translations_description
                FROM sjw_equipment_set_translations
                WHERE sjw_equipment_set_translations_equipment_sets_id = %s AND sjw_equipment_set_translations_language = %s
            """, (set_id, language))
            desc_row = self.cursor.fetchone()
            set_description = desc_row[0] if desc_row else ""
            # Focus stats
            self.cursor.execute("""
                SELECT sjw_equipment_focus_stats_name
                FROM sjw_equipment_focus_stats
                WHERE sjw_equipment_focus_stats_sjw_equipment_sets_id = %s
            """, (set_id,))
            focus_stats = [fs_row[0] for fs_row in self.cursor.fetchall()]
            # Artefacts
            self.cursor.execute("""
                SELECT a.sjw_artefacts_id, a.sjw_artefacts_image, a.sjw_artefacts_main_stat, a.sjw_artefacts_number, a.sjw_artefacts_set
                FROM sjw_artefacts a
                WHERE a.sjw_artefacts_sjw_equipment_sets_id = %s
                ORDER BY a.sjw_artefacts_number
            """, (set_id,))
            artefacts = []
            for a_row in self.cursor.fetchall():
                artefact_id, artefact_image, artefact_main_stat, artefact_number, artefact_set = a_row
                # Traduction
                self.cursor.execute("""
                    SELECT sjw_artefact_translations_language, sjw_artefact_translations_name
                    FROM sjw_artefact_translations
                    WHERE sjw_artefact_translations_sjw_artefacts_id = %s
                """, (artefact_id,))
                translations = {lang: {'name': name} for lang, name in self.cursor.fetchall()}
                # Secondary stats
                self.cursor.execute("""
                    SELECT sjw_artefact_secondary_stats_name
                    FROM sjw_artefact_secondary_stats
                    WHERE sjw_artefact_secondary_stats_sjw_artefacts_id = %s
                """, (artefact_id,))
                secondary_stats = [sec_row[0] for sec_row in self.cursor.fetchall()]
                artefacts.append({
                    'id': artefact_id,
                    'name': translations.get(language, {}).get('name', ''),
                    'set': artefact_set,
                    'image_name': artefact_image,
                    'main_stat': artefact_main_stat,
                    'secondary_stats': secondary_stats,
                    'number': artefact_number,
                    'translations': translations
                })
            # Cores
            self.cursor.execute("""
                SELECT c.sjw_cores_id, c.sjw_cores_name, c.sjw_cores_number, c.sjw_cores_image, c.sjw_cores_main_stat, c.sjw_cores_secondary_stat
                FROM sjw_cores c
                WHERE c.sjw_cores_sjw_equipment_sets_id = %s
                ORDER BY c.sjw_cores_number
            """, (set_id,))
            cores = []
            for c_row in self.cursor.fetchall():
                cores.append({
                    'id': c_row[0],
                    'name': c_row[1],
                    'number': c_row[2],
                    'image_name': c_row[3],
                    'main_stat': c_row[4],
                    'secondary_stat': c_row[5]
                })
            sets.append({
                'id': set_id,
                'name': set_name,
                'description': set_description,
                'focus_stats': focus_stats,
                'artefacts': artefacts,
                'cores': cores
            })
        return sets