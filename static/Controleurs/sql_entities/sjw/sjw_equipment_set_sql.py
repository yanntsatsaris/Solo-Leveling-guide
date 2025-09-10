from collections import Counter
from static.Controleurs.ControleurLog import write_log
import re

class SJWEquipmentSetSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_equipment_sets(self, sjw_id, language):
        write_log(f"Requête get_equipment_sets pour sjw_id={sjw_id}, language={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT es.sjw_equipment_sets_id, es.sjw_equipment_sets_name
            FROM sjw_equipment_sets es
            WHERE es.sjw_equipment_sets_sjw_id = %s
            ORDER BY es.sjw_equipment_sets_id ASC
        """, (sjw_id,))
        return self.cursor.fetchall()

    def get_equipment_set_details(self, eq_set_id, eq_set_name, language):
        write_log(f"Requête get_equipment_set_details pour eq_set_id={eq_set_id}, language={language}", log_level="DEBUG")
        # Description traduite du set
        self.cursor.execute("""
            SELECT sjw_equipment_set_translations_description
            FROM sjw_equipment_set_translations
            WHERE sjw_equipment_set_translations_equipment_sets_id = %s AND sjw_equipment_set_translations_language = %s
        """, (eq_set_id, language))
        desc_row = self.cursor.fetchone()
        set_description = desc_row[0] if desc_row else ""
        # Focus stats
        self.cursor.execute("""
            SELECT sjw_equipment_focus_stats_name FROM sjw_equipment_focus_stats
            WHERE sjw_equipment_focus_stats_sjw_equipment_sets_id = %s
        """, (eq_set_id,))
        focus_stats = [fs_row[0] for fs_row in self.cursor.fetchall()]
        # Artefacts
        self.cursor.execute("""
            SELECT a.sjw_artefacts_id, a.sjw_artefacts_image, a.sjw_artefacts_main_stat, a.sjw_artefacts_number
            FROM sjw_artefacts a
            WHERE a.sjw_artefacts_sjw_equipment_sets_id = %s
            ORDER BY a.sjw_artefacts_number
        """, (eq_set_id,))
        artefacts = []
        artefact_sets = []
        for a_row in self.cursor.fetchall():
            artefact_id, artefact_image, artefact_main_stat, artefact_set = a_row
            # Récupère toutes les traductions de cet artefact
            self.cursor.execute("""
                SELECT sjw_artefact_translations_language, sjw_artefact_translations_name
                FROM sjw_artefact_translations
                WHERE sjw_artefact_translations_sjw_artefacts_id = %s
            """, (artefact_id,))
            translations = {}
            for lang, name in self.cursor.fetchall():
                translations[lang] = {'name': name}
            # Récupère les secondary_stats
            self.cursor.execute("""
                SELECT sjw_artefact_secondary_stats_name FROM sjw_artefact_secondary_stats
                WHERE sjw_artefact_secondary_stats_sjw_artefacts_id = %s
            """, (artefact_id,))
            secondary_stats = [sec_row[0] for sec_row in self.cursor.fetchall()]
            # Pour compatibilité, on peut garder la traduction dans la langue demandée
            artefact_name = translations.get(language, {}).get('name', '')
            artefact_set_path = artefact_set.replace(" ", "_") if artefact_set else ""
            artefact_obj = {
                'id': artefact_id,
                'name': artefact_name,
                'set': artefact_set,
                'image': f'images/Artefacts/{artefact_set_path}/{artefact_image}' if artefact_image else '',
                'image_name': artefact_image,
                'main_stat': artefact_main_stat,
                'secondary_stats': secondary_stats,
                'translations': translations
            }
            artefacts.append(artefact_obj)
            artefact_sets.append(artefact_set)
        # Noyaux
        self.cursor.execute("""
            SELECT c.sjw_cores_id, c.sjw_cores_name, c.sjw_cores_number, c.sjw_cores_image, c.sjw_cores_main_stat, c.sjw_cores_secondary_stat
            FROM sjw_cores c
            WHERE c.sjw_cores_sjw_equipment_sets_id = %s
            ORDER BY c.sjw_cores_number
        """, (eq_set_id,))
        cores = []
        for core_row in self.cursor.fetchall():
            core_obj = {
                'id': core_row[0],
                'name': core_row[1],
                'number': core_row[2],
                'image': f'images/Noyaux/{core_row[3]}' if core_row[3] else '',
                'image_name': core_row[3],
                'main_stat': core_row[4],
                'secondary_stat': core_row[5]
            }
            cores.append(core_obj)
        # Dictionnaire d'ordre des artefacts par langue
        artefact_types = {
            'FR-fr': ['Casque', 'Plastron', 'Gants', 'Bottes', 'Collier', 'Bracelet', 'Bague', "Boucle d'oreille"],
            'EN-en': ['Helmet', 'Chestplate', 'Gloves', 'Boots', 'Necklace', 'Bracelet', 'Ring', 'Earring']
        }
        artefact_type_list = artefact_types.get(language, artefact_types['FR-fr'])
        
         # Construction de la liste artefacts
        artefacts_sorted = []
        for type_name in artefact_type_list:
            found = next((a for a in artefacts if a['name'] == type_name), None)
            if found:
                artefacts_sorted.append(found)

        set_piece_count = Counter(artefact_sets)
        return {
            'id': eq_set_id,
            'set_name': eq_set_name,
            'description': set_description,
            'focus_stats': focus_stats,
            'artefacts': artefacts,
            'cores': cores,
            'set_piece_count': dict(set_piece_count)
        }

    def get_equipment_sets_full(self, sjw_id, language):
        self.cursor.execute("""
            SELECT es.sjw_equipment_sets_id, es.sjw_equipment_sets_name, est.sjw_equipment_set_translations_description
            FROM sjw_equipment_sets es
            LEFT JOIN sjw_equipment_set_translations est ON est.sjw_equipment_set_translations_equipment_sets_id = es.sjw_equipment_sets_id AND est.sjw_equipment_set_translations_language = %s
            WHERE es.sjw_equipment_sets_sjw_id = %s
            ORDER BY es.sjw_equipment_sets_id ASC
        """, (language, sjw_id))
        sets = []
        for row in self.cursor.fetchall():
            set_id, set_name, set_desc = row
            # Focus stats
            self.cursor.execute("""
                SELECT sjw_equipment_focus_stats_name
                FROM sjw_equipment_focus_stats
                WHERE sjw_equipment_focus_stats_sjw_equipment_sets_id = %s
            """, (set_id,))
            focus_stats = [fs_row[0] for fs_row in self.cursor.fetchall()]
            # Artefacts
            self.cursor.execute("""
                SELECT a.sjw_artefacts_id, a.sjw_artefacts_image, a.sjw_artefacts_main_stat, a.sjw_artefacts_number
                FROM sjw_artefacts a
                WHERE a.sjw_artefacts_sjw_equipment_sets_id = %s
                ORDER BY a.sjw_artefacts_number
            """, (set_id,))
            artefacts = []
            for a_row in self.cursor.fetchall():
                artefact_id, artefact_image, artefact_main_stat, artefact_number = a_row
                # Récupère toutes les traductions de cet artefact
                self.cursor.execute("""
                    SELECT sjw_artefact_translations_language, sjw_artefact_translations_name
                    FROM sjw_artefact_translations
                    WHERE sjw_artefact_translations_sjw_artefacts_id = %s
                """, (artefact_id,))
                translations = {}
                for lang, name in self.cursor.fetchall():
                    translations[lang] = {'name': name}
                # Récupère les secondary_stats
                self.cursor.execute("""
                    SELECT sjw_artefact_secondary_stats_name FROM sjw_artefact_secondary_stats
                    WHERE sjw_artefact_secondary_stats_sjw_artefacts_id = %s
                """, (artefact_id,))
                secondary_stats = [sec_row[0] for sec_row in self.cursor.fetchall()]
                # Set de l'artefact
                self.cursor.execute("""
                    SELECT sjw_artefact_translations_set
                    FROM sjw_artefact_translations
                    WHERE sjw_artefact_translations_sjw_artefacts_id = %s AND sjw_artefact_translations_language = %s
                """, (artefact_id, language))
                set_row = self.cursor.fetchone()
                artefact_set = set_row[0] if set_row else ""
                artefact_set_path = artefact_set.replace(" ", "_") if artefact_set else ""
                artefacts.append({
                    'id': artefact_id,
                    'name': translations.get(language, {}).get('name', ''),
                    'set': artefact_set,
                    'image': f'images/Artefacts/{artefact_set_path}/{artefact_image}' if artefact_image else '',
                    'image_name': artefact_image,
                    'main_stat': artefact_main_stat,
                    'secondary_stats': secondary_stats,
                    'number': artefact_number,
                    'translations': translations
                })
            # Noyaux
            self.cursor.execute("""
                SELECT c.sjw_cores_id, c.sjw_cores_name, c.sjw_cores_number, c.sjw_cores_image, c.sjw_cores_main_stat, c.sjw_cores_secondary_stat
                FROM sjw_cores c
                WHERE c.sjw_cores_sjw_equipment_sets_id = %s
                ORDER BY c.sjw_cores_number
            """, (set_id,))
            cores = []
            for core_row in self.cursor.fetchall():
                cores.append({
                    'id': core_row[0],
                    'name': core_row[1],
                    'number': core_row[2],
                    'image': f'images/Noyaux/{core_row[3]}' if core_row[3] else '',
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