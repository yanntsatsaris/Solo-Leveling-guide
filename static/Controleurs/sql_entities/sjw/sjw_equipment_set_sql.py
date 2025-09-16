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
            ORDER BY es.sjw_equipment_sets_order ASC, es.sjw_equipment_sets_id ASC
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
            SELECT a.sjw_artefacts_id, a.sjw_artefacts_image, a.sjw_artefacts_main_stat, a.sjw_artefacts_set
            FROM sjw_artefacts a
            WHERE a.sjw_artefacts_sjw_equipment_sets_id = %s
            ORDER BY a.sjw_artefacts_image
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
            SELECT es.sjw_equipment_sets_id, es.sjw_equipment_sets_name, est.sjw_equipment_set_translations_description, es.sjw_equipment_sets_order
            FROM sjw_equipment_sets es
            LEFT JOIN sjw_equipment_set_translations est ON est.sjw_equipment_set_translations_equipment_sets_id = es.sjw_equipment_sets_id AND est.sjw_equipment_set_translations_language = %s
            WHERE es.sjw_equipment_sets_sjw_id = %s
            ORDER BY es.sjw_equipment_sets_order ASC, es.sjw_equipment_sets_id ASC
        """, (language, sjw_id))
        sets = []
        # Dictionnaire d'ordre des artefacts par langue
        artefact_types = {
            'FR-fr': ['Casque', 'Plastron', 'Gants', 'Bottes', 'Collier', 'Bracelet', 'Bague', "Boucle d'oreille"],
            'EN-en': ['Helmet', 'Chestplate', 'Gloves', 'Boots', 'Necklace', 'Bracelet', 'Ring', 'Earring']
        }
        artefact_type_list = artefact_types.get(language, artefact_types['FR-fr'])

        for row in self.cursor.fetchall():
            set_id, set_name, set_desc, set_order = row
            # Focus stats (récupère toutes les stats pour ce set)
            self.cursor.execute("""
                SELECT sjw_equipment_focus_stats_name FROM sjw_equipment_focus_stats
                WHERE sjw_equipment_focus_stats_sjw_equipment_sets_id = %s
            """, (set_id,))
            focus_stats = [fs_row[0] for fs_row in self.cursor.fetchall()]
            # Artefacts
            self.cursor.execute("""
                SELECT a.sjw_artefacts_id, a.sjw_artefacts_image, a.sjw_artefacts_main_stat, a.sjw_artefacts_set
                FROM sjw_artefacts a
                WHERE a.sjw_artefacts_sjw_equipment_sets_id = %s
                ORDER by a.sjw_artefacts_image
            """, (set_id,))
            artefacts = []
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
                artefacts.append({
                    'id': artefact_id,
                    'name': translations.get(language, {}).get('name', ''),
                    'set': artefact_set,
                    'image_name': artefact_image,
                    'main_stat': artefact_main_stat,
                    'secondary_stats': secondary_stats
                })
            # Trie les artefacts selon l'ordre défini
            artefacts_sorted = []
            for type_name in artefact_type_list:
                found = next((a for a in artefacts if a['name'] == type_name), None)
                if found:
                    artefacts_sorted.append(found)
            # Noyaux
            self.cursor.execute("""
                SELECT sjw_cores_id, sjw_cores_name, sjw_cores_number, sjw_cores_image, sjw_cores_main_stat, sjw_cores_secondary_stat
                FROM sjw_cores
                WHERE sjw_cores_sjw_equipment_sets_id = %s
                ORDER BY sjw_cores_number
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
                'artefacts': artefacts,  # <-- liste triée
                'cores': cores,
                'order': set_order
            })
        return sets

    def update_equipment_set(self, set_id, char_id, name, desc, focus, order, language):
        self.cursor.execute("""
            UPDATE sjw_equipment_sets SET sjw_equipment_sets_name=%s, sjw_equipment_sets_order=%s WHERE sjw_equipment_sets_id=%s
        """, (name, order, set_id))
        self.cursor.execute("""
            DELETE FROM sjw_equipment_focus_stats WHERE sjw_equipment_focus_stats_sjw_equipment_sets_id=%s
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
                    INSERT INTO sjw_equipment_focus_stats (sjw_equipment_focus_stats_sjw_equipment_sets_id, sjw_equipment_focus_stats_name)
                    VALUES (%s, %s)
                """, (set_id, stat))
        # Vérifie si la traduction existe déjà
        self.cursor.execute("""
            SELECT 1 FROM sjw_equipment_set_translations
            WHERE sjw_equipment_set_translations_equipment_sets_id=%s AND sjw_equipment_set_translations_language=%s
        """, (set_id, language))
        if self.cursor.fetchone():
            self.cursor.execute("""
                UPDATE sjw_equipment_set_translations SET sjw_equipment_set_translations_description=%s
                WHERE sjw_equipment_set_translations_sjw_equipment_sets_id=%s AND sjw_equipment_set_translations_language=%s
            """, (desc, set_id, language))
        else:
            self.cursor.execute("""
                INSERT INTO sjw_equipment_set_translations (sjw_equipment_set_translations_sjw_equipment_sets_id, sjw_equipment_set_translations_language, sjw_equipment_set_translations_description)
                VALUES (%s, %s, %s)
            """, (set_id, language, desc))

    def add_equipment_set(self, char_id, name, desc, focus, order, language):
        self.cursor.execute("""
            INSERT INTO sjw_equipment_sets (sjw_equipment_sets_sjw_id, sjw_equipment_sets_name, sjw_equipment_sets_order)
            VALUES (%s, %s, %s) RETURNING sjw_equipment_sets_id
        """, (char_id, name, order))
        set_id = self.cursor.fetchone()[0]
        self.cursor.execute("""
            INSERT INTO sjw_equipment_set_translations (sjw_equipment_set_translations_sjw_equipment_sets_id, sjw_equipment_set_translations_language, sjw_equipment_set_translations_description)
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
                    INSERT INTO sjw_equipment_focus_stats (sjw_equipment_focus_stats_sjw_equipment_sets_id, sjw_equipment_focus_stats_name)
                    VALUES (%s, %s)
                """, (set_id, stat))
        return set_id
    
    def delete_equipment_set(self, set_id):
        # Supprimer d'abord les stats secondaires des artefacts du set
        self.cursor.execute("""
            DELETE FROM sjw_artefact_secondary_stats
            WHERE sjw_artefact_secondary_stats_artefacts_id IN (
                SELECT sjw_artefacts_id FROM sjw_artefacts WHERE sjw_artefacts_equipment_sets_id=%s
            )
        """, (set_id,))
        # Supprimer d'abord les traductions des artefacts du set
        self.cursor.execute("""
            DELETE FROM sjw_artefact_translations
            WHERE sjw_artefact_translations_artefacts_id IN (
                SELECT sjw_artefacts_id FROM sjw_artefacts WHERE sjw_artefacts_equipment_sets_id=%s
            )
        """, (set_id,))
        # Supprimer les artefacts du set
        self.cursor.execute("DELETE FROM sjw_artefacts WHERE sjw_artefacts_equipment_sets_id=%s", (set_id,))
        # Supprimer les noyaux du set
        self.cursor.execute("DELETE FROM sjw_cores WHERE sjw_cores_equipment_sets_id=%s", (set_id,))
        # Supprimer les stats de focus
        self.cursor.execute("DELETE FROM sjw_equipment_focus_stats WHERE sjw_equipment_focus_stats_sjw_equipment_sets_id=%s", (set_id,))
        # Supprimer les traductions du set
        self.cursor.execute("DELETE FROM sjw_equipment_set_translations WHERE sjw_equipment_set_translations_sjw_equipment_sets_id=%s", (set_id,))
        # Supprimer le set lui-même
        self.cursor.execute("DELETE FROM sjw_equipment_sets WHERE sjw_equipment_sets_id=%s", (set_id,))
    
    def update_artefact(self, aid, set_id, name, aset, img, main, sec, language):
        self.cursor.execute("""
            UPDATE sjw_artefacts SET sjw_artefacts_image=%s, sjw_artefacts_main_stat=%s, sjw_artefacts_set=%s WHERE sjw_artefacts_id=%s
        """, (img, main, aset, aid))
        # Vérifie si la traduction existe déjà
        self.cursor.execute("""
            SELECT 1 FROM sjw_artefact_translations
            WHERE sjw_artefact_translations_sjw_artefacts_id=%s AND sjw_artefact_translations_language=%s
        """, (aid, language))
        if self.cursor.fetchone():
            self.cursor.execute("""
                UPDATE sjw_artefact_translations SET sjw_artefact_translations_name=%s
                WHERE sjw_artefact_translations_sjw_artefacts_id=%s AND sjw_artefact_translations_language=%s
            """, (name, aid, language))
        else:
            self.cursor.execute("""
                INSERT INTO sjw_artefact_translations (sjw_artefact_translations_sjw_artefacts_id, sjw_artefact_translations_language, sjw_artefact_translations_name)
                VALUES (%s, %s, %s)
            """, (aid, language, name))
        self.cursor.execute("""
            DELETE FROM sjw_artefact_secondary_stats WHERE sjw_artefact_secondary_stats_sjw_artefacts_id=%s
        """, (aid,))
        if sec:
            for stat in sec.split(','):
                self.cursor.execute("""
                    INSERT INTO sjw_artefact_secondary_stats (sjw_artefact_secondary_stats_sjw_artefacts_id, sjw_artefact_secondary_stats_name)
                    VALUES (%s, %s)
                """, (aid, stat.strip()))

    def add_artefact(self, set_id, name, aset, img, main, sec, language):
        # Recherche d'un artefact existant pour ce set avec la même image et main_stat
        self.cursor.execute("""
            SELECT sjw_artefacts_id FROM sjw_artefacts
            WHERE sjw_artefacts_equipment_sets_id=%s AND sjw_artefacts_image=%s AND sjw_artefacts_main_stat=%s AND sjw_artefacts_set=%s
        """, (set_id, img, main, aset))
        row = self.cursor.fetchone()
        if row:
            aid = row[0]
            # Vérifie si la traduction existe déjà
            self.cursor.execute("""
                SELECT 1 FROM sjw_artefact_translations
                WHERE sjw_artefact_translations_sjw_artefacts_id=%s AND sjw_artefact_translations_language=%s
            """, (aid, language))
            if not self.cursor.fetchone():
                self.cursor.execute("""
                    INSERT INTO sjw_artefact_translations (sjw_artefact_translations_sjw_artefacts_id, sjw_artefact_translations_language, sjw_artefact_translations_name)
                    VALUES (%s, %s, %s)
                """, (aid, language, name))
            # Mets à jour les secondary_stats si besoin
            self.cursor.execute("DELETE FROM sjw_artefact_secondary_stats WHERE sjw_artefact_secondary_stats_sjw_artefacts_id=%s", (aid,))
            if sec:
                for stat in sec.split(','):
                    self.cursor.execute("""
                        INSERT INTO sjw_artefact_secondary_stats (sjw_artefact_secondary_stats_sjw_artefacts_id, sjw_artefact_secondary_stats_name)
                        VALUES (%s, %s)
                    """, (aid, stat.strip()))
            return aid
        else:
            # Création normale
            self.cursor.execute("""
                INSERT INTO sjw_artefacts (sjw_artefacts_equipment_sets_id, sjw_artefacts_image, sjw_artefacts_main_stat, sjw_artefacts_set)
                VALUES (%s, %s, %s, %s) RETURNING sjw_artefacts_id
            """, (set_id, img, main, aset))
            aid = self.cursor.fetchone()[0]
            self.cursor.execute("""
                INSERT INTO sjw_artefact_translations (sjw_artefact_translations_sjw_artefacts_id, sjw_artefact_translations_language, sjw_artefact_translations_name)
                VALUES (%s, %s, %s)
            """, (aid, language, name))
            if sec:
                for stat in sec.split(','):
                    self.cursor.execute("""
                        INSERT INTO sjw_artefact_secondary_stats (sjw_artefact_secondary_stats_sjw_artefacts_id, sjw_artefact_secondary_stats_name)
                        VALUES (%s, %s)
                    """, (aid, stat.strip()))
            return aid

    def delete_artefact(self, aid):
        self.cursor.execute("DELETE FROM sjw_artefact_secondary_stats WHERE sjw_artefact_secondary_stats_sjw_artefacts_id=%s", (aid,))
        self.cursor.execute("DELETE FROM sjw_artefact_translations WHERE sjw_artefact_translations_sjw_artefacts_id=%s", (aid,))
        self.cursor.execute("DELETE FROM sjw_artefacts WHERE sjw_artefacts_id=%s", (aid,))

    def update_core(self, cid, set_id, name, img, main, sec, number, language):
        self.cursor.execute("""
            UPDATE sjw_cores
            SET sjw_cores_name=%s, sjw_cores_image=%s, sjw_cores_main_stat=%s, sjw_cores_secondary_stat=%s, sjw_cores_sjw_equipment_sets_id=%s, sjw_cores_number=%s
            WHERE sjw_cores_id=%s
        """, (name, img, main, sec, set_id, number, cid))

    def add_core(self, set_id, name, img, main, sec, number, language):
        self.cursor.execute("""
            INSERT INTO sjw_cores (sjw_cores_sjw_equipment_sets_id, sjw_cores_name, sjw_cores_image, sjw_cores_main_stat, sjw_cores_secondary_stat, sjw_cores_number)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING sjw_cores_id
        """, (set_id, name, img, main, sec, number))
        return self.cursor.fetchone()[0]

    def delete_core(self, cid):
        self.cursor.execute("DELETE FROM sjw_cores WHERE sjw_cores_id=%s", (cid,))