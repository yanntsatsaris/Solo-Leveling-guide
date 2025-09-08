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
            # Artefacts
            self.cursor.execute("""
                SELECT a.sjw_artefacts_id, a.sjw_artefacts_number, a.sjw_artefacts_image, a.sjw_artefacts_main_stat
                FROM sjw_artefacts a
                WHERE a.sjw_artefacts_sjw_equipment_sets_id = %s
                ORDER BY a.sjw_artefacts_number
            """, (set_id,))
            artefacts = []
            for a_row in self.cursor.fetchall():
                artefacts.append({
                    'id': a_row[0],
                    'number': a_row[1],
                    'image': a_row[2],
                    'main_stat': a_row[3]
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
                    'image': c_row[3],
                    'main_stat': c_row[4],
                    'secondary_stat': c_row[5]
                })
            sets.append({
                'id': set_id,
                'name': set_name,
                'artefacts': artefacts,
                'cores': cores
            })
        return sets