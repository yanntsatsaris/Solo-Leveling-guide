from collections import Counter
from static.Controleurs.ControleurLog import write_log
import re

class EquipmentSetSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_equipment_sets(self, char_id, language):
        write_log(f"Requête get_equipment_sets pour char_id={char_id}, langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT es.equipment_sets_id, es.equipment_sets_name
            FROM equipment_sets es
            WHERE es.equipment_sets_characters_id = %s
            ORDER BY es.equipment_sets_order ASC, es.equipment_sets_id ASC
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
            # Remplacement des espaces par des "_" dans artefact_set pour le chemin image
            artefact_set_path = artefact_set.replace(" ", "_") if artefact_set else ""
            artefact_obj = {
                'id': artefact_id,  # <-- AJOUT DE L'ID
                'name': artefact_name,
                'set': artefact_set,
                'image': f'images/Artefacts/{artefact_set_path}/{artefact_image}' if artefact_image else '',
                'image_name': artefact_image,
                'main_stat': artefact_main_stat,
                'secondary_stats': secondary_stats
            }
            artefacts.append(artefact_obj)
            artefact_sets.append(artefact_set)
        # Noyaux
        self.cursor.execute("""
            SELECT cores_id, cores_name, cores_number, cores_image, cores_main_stat, cores_secondary_stat
            FROM cores
            WHERE cores_equipment_sets_id = %s
        """, (eq_set_id,))
        cores = []
        for core_row in self.cursor.fetchall():
            core_obj = {
                'id': core_row[0],  # <-- AJOUT DE L'ID
                'name': core_row[1],
                'number': core_row[2],
                'image': f'images/Noyaux/{core_row[3]}' if core_row[3] else '',
                'image_name': core_row[3],
                'main_stat': core_row[4],
                'secondary_stat': core_row[5]
            }
            cores.append(core_obj)
        set_piece_count = Counter(artefact_sets)
        return {
            'id': eq_set_id,  # <-- AJOUT DE L'ID DU SET
            'set_name': eq_set_name,
            'description': set_description,
            'focus_stats': focus_stats,
            'artefacts': artefacts,
            'cores': cores,
            'set_piece_count': dict(set_piece_count)
        }

    def get_equipment_sets_full(self, char_id, language):
        self.cursor.execute("""
            SELECT es.equipment_sets_id, es.equipment_sets_name, est.equipment_set_translations_description
            FROM equipment_sets es
            LEFT JOIN equipment_set_translations est ON est.equipment_set_translations_equipment_sets_id = es.equipment_sets_id AND est.equipment_set_translations_language = %s
            WHERE es.equipment_sets_characters_id = %s
            ORDER BY es.equipment_sets_order ASC, es.equipment_sets_id ASC
        """, (language, char_id))
        sets = []
        for row in self.cursor.fetchall():
            set_id, set_name, set_desc = row
            # Focus stats (récupère toutes les stats pour ce set)
            self.cursor.execute("""
                SELECT equipment_focus_stats_name FROM equipment_focus_stats
                WHERE equipment_focus_stats_equipment_sets_id = %s
            """, (set_id,))
            focus_stats = [fs_row[0] for fs_row in self.cursor.fetchall()]
            # Artefacts
            self.cursor.execute("""
                SELECT a.artefacts_id, at.artefact_translations_name, at.artefact_translations_set, a.artefacts_image, a.artefacts_main_stat
                FROM artefacts a
                JOIN artefact_translations at ON at.artefact_translations_artefacts_id = a.artefacts_id
                WHERE a.artefacts_equipment_sets_id = %s AND at.artefact_translations_language = %s
            """, (set_id, language))
            artefacts = []
            for a_row in self.cursor.fetchall():
                artefact_id, artefact_name, artefact_set, artefact_image, artefact_main_stat = a_row
                self.cursor.execute("""
                    SELECT artefact_secondary_stats_name FROM artefact_secondary_stats
                    WHERE artefact_secondary_stats_artefacts_id = %s
                """, (artefact_id,))
                secondary_stats = [sec_row[0] for sec_row in self.cursor.fetchall()]
                artefacts.append({
                    'id': artefact_id,
                    'name': artefact_name,
                    'set': artefact_set,
                    'image_name': artefact_image,
                    'main_stat': artefact_main_stat,
                    'secondary_stats': secondary_stats
                })
            # Noyaux
            self.cursor.execute("""
                SELECT cores_id, cores_name, cores_number, cores_image, cores_main_stat, cores_secondary_stat
                FROM cores
                WHERE cores_equipment_sets_id = %s
            """, (set_id,))
            cores = []
            for core_row in self.cursor.fetchall():
                cores.append({
                    'id': core_row[0],
                    'name': core_row[1],
                    'number': core_row[2],
                    'image_name': core_row[3],
                    'main_stat': core_row[4],
                    'secondary_stat': core_row[5]
                })
            sets.append({
                'id': set_id,
                'name': set_name,
                'description': set_desc,
                'focus_stats': focus_stats,
                'artefacts': artefacts,
                'cores': cores
            })
        return sets

    def update_equipment_set(self, set_id, char_id, name, desc, focus, language):
        self.cursor.execute("""
            UPDATE equipment_sets SET equipment_sets_name=%s WHERE equipment_sets_id=%s
        """, (name, set_id))
        self.cursor.execute("""
            UPDATE equipment_set_translations SET equipment_set_translations_description=%s
            WHERE equipment_set_translations_equipment_sets_id=%s AND equipment_set_translations_language=%s
        """, (desc, set_id, language))
        self.cursor.execute("""
            DELETE FROM equipment_focus_stats WHERE equipment_focus_stats_equipment_sets_id=%s
        """, (set_id,))
        if focus:
            if isinstance(focus, str):
                focus_stats = [f.strip() for f in focus.split(',') if f.strip()]
            elif isinstance(focus, list):
                focus_stats = focus
            else:
                focus_stats = []
            for stat in focus_stats:
                self.cursor.execute("""
                    INSERT INTO equipment_focus_stats (equipment_focus_stats_equipment_sets_id, equipment_focus_stats_name)
                    VALUES (%s, %s)
                """, (set_id, stat))

    def add_equipment_set(self, char_id, name, desc, focus, language):
        self.cursor.execute("""
            INSERT INTO equipment_sets (equipment_sets_characters_id, equipment_sets_name)
            VALUES (%s, %s) RETURNING equipment_sets_id
        """, (char_id, name))
        set_id = self.cursor.fetchone()[0]
        self.cursor.execute("""
            INSERT INTO equipment_set_translations (equipment_set_translations_equipment_sets_id, equipment_set_translations_language, equipment_set_translations_description)
            VALUES (%s, %s, %s)
        """, (set_id, language, desc))
        if focus:
            if isinstance(focus, str):
                focus_stats = [f.strip() for f in focus.split(',') if f.strip()]
            elif isinstance(focus, list):
                focus_stats = focus
            else:
                focus_stats = []
            for stat in focus_stats:
                self.cursor.execute("""
                    INSERT INTO equipment_focus_stats (equipment_focus_stats_equipment_sets_id, equipment_focus_stats_name)
                    VALUES (%s, %s)
                """, (set_id, stat))
        return set_id

    def delete_equipment_set(self, set_id):
        # Supprimer d'abord les stats secondaires des artefacts du set
        self.cursor.execute("""
            DELETE FROM artefact_secondary_stats
            WHERE artefact_secondary_stats_artefacts_id IN (
                SELECT artefacts_id FROM artefacts WHERE artefacts_equipment_sets_id=%s
            )
        """, (set_id,))
        # Supprimer d'abord les traductions des artefacts du set
        self.cursor.execute("""
            DELETE FROM artefact_translations
            WHERE artefact_translations_artefacts_id IN (
                SELECT artefacts_id FROM artefacts WHERE artefacts_equipment_sets_id=%s
            )
        """, (set_id,))
        # Supprimer les artefacts du set
        self.cursor.execute("DELETE FROM artefacts WHERE artefacts_equipment_sets_id=%s", (set_id,))
        # Supprimer les noyaux du set
        self.cursor.execute("DELETE FROM cores WHERE cores_equipment_sets_id=%s", (set_id,))
        # Supprimer les stats de focus
        self.cursor.execute("DELETE FROM equipment_focus_stats WHERE equipment_focus_stats_equipment_sets_id=%s", (set_id,))
        # Supprimer les traductions du set
        self.cursor.execute("DELETE FROM equipment_set_translations WHERE equipment_set_translations_equipment_sets_id=%s", (set_id,))
        # Supprimer le set lui-même
        self.cursor.execute("DELETE FROM equipment_sets WHERE equipment_sets_id=%s", (set_id,))

    def update_artefact(self, aid, set_id, name, aset, img, main, sec, language):
        self.cursor.execute("""
            UPDATE artefacts SET artefacts_image=%s, artefacts_main_stat=%s WHERE artefacts_id=%s
        """, (img, main, aid))
        self.cursor.execute("""
            UPDATE artefact_translations SET artefact_translations_name=%s, artefact_translations_set=%s
            WHERE artefact_translations_artefacts_id=%s AND artefact_translations_language=%s
        """, (name, aset, aid, language))
        self.cursor.execute("""
            DELETE FROM artefact_secondary_stats WHERE artefact_secondary_stats_artefacts_id=%s
        """, (aid,))
        if sec:
            for stat in sec.split(','):
                self.cursor.execute("""
                    INSERT INTO artefact_secondary_stats (artefact_secondary_stats_artefacts_id, artefact_secondary_stats_name)
                    VALUES (%s, %s)
                """, (aid, stat.strip()))

    def add_artefact(self, set_id, name, aset, img, main, sec, language):
        self.cursor.execute("""
            INSERT INTO artefacts (artefacts_equipment_sets_id, artefacts_image, artefacts_main_stat)
            VALUES (%s, %s, %s) RETURNING artefacts_id
        """, (set_id, img, main))
        aid = self.cursor.fetchone()[0]
        self.cursor.execute("""
            INSERT INTO artefact_translations (artefact_translations_artefacts_id, artefact_translations_language, artefact_translations_name, artefact_translations_set)
            VALUES (%s, %s, %s, %s)
        """, (aid, language, name, aset))
        if sec:
            for stat in sec.split(','):
                self.cursor.execute("""
                    INSERT INTO artefact_secondary_stats (artefact_secondary_stats_artefacts_id, artefact_secondary_stats_name)
                    VALUES (%s, %s)
                """, (aid, stat.strip()))
        return aid

    def delete_artefact(self, aid):
        self.cursor.execute("DELETE FROM artefact_secondary_stats WHERE artefact_secondary_stats_artefacts_id=%s", (aid,))
        self.cursor.execute("DELETE FROM artefact_translations WHERE artefact_translations_artefacts_id=%s", (aid,))
        self.cursor.execute("DELETE FROM artefacts WHERE artefacts_id=%s", (aid,))

    def update_core(self, cid, set_id, name, img, main, sec, language):
        self.cursor.execute("""
            UPDATE cores
            SET cores_name=%s, cores_image=%s, cores_main_stat=%s, cores_secondary_stat=%s, cores_equipment_sets_id=%s
            WHERE cores_id=%s
        """, (name, img, main, sec, set_id, cid))

    def add_core(self, set_id, name, img, main, sec, language):
        self.cursor.execute("""
            INSERT INTO cores (cores_equipment_sets_id, cores_name, cores_image, cores_main_stat, cores_secondary_stat)
            VALUES (%s, %s, %s, %s, %s) RETURNING cores_id
        """, (set_id, name, img, main, sec))
        return self.cursor.fetchone()[0]

    def delete_core(self, cid):
        self.cursor.execute("DELETE FROM cores WHERE cores_id=%s", (cid,))