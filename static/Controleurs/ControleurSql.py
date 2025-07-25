import psycopg2
from collections import Counter
from static.Controleurs.ControleurConf import ControleurConf

class ControleurSql:
    def __init__(self):
        conf = ControleurConf()
        database = conf.get_config('PSQL', 'database')
        user = conf.get_config('PSQL', 'user')
        password = conf.get_config('PSQL', 'password')
        self.conn = psycopg2.connect(
            dbname=database,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

    def get_characters(self, language):
        self.cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder, ct.character_translations_name
            FROM characters c
            JOIN character_translations ct ON ct.character_translations_characters_id = c.characters_id
            WHERE ct.character_translations_language = %s
        """, (language,))
        return self.cursor.fetchall()

    def get_panoplies(self, language):
        self.cursor.execute("""
            SELECT p.panoplies_name, pt.panoplie_translations_name, pt.panoplie_translations_language
            FROM panoplies p
            JOIN panoplie_translations pt ON pt.panoplie_translations_panoplies_id = p.panoplies_id
            WHERE pt.panoplie_translations_language = %s
        """, (language,))
        return self.cursor.fetchall()

    def get_character_details(self, language, alias):
        self.cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder, ct.character_translations_name, ct.character_translations_description
            FROM characters c
            JOIN character_translations ct ON ct.character_translations_characters_id = c.characters_id
            WHERE ct.character_translations_language = %s AND c.characters_alias = %s
        """, (language, alias))
        return self.cursor.fetchone()

    def get_passives(self, char_id, language, type_folder, char_folder, update_image_paths):
        self.cursor.execute("""
            SELECT p.passives_principal, pt.passive_translations_name, pt.passive_translations_description, p.passives_image
            FROM passives p
            JOIN passive_translations pt ON pt.passive_translations_passives_id = p.passives_id
            WHERE p.passives_characters_id = %s AND pt.passive_translations_language = %s
        """, (char_id, language))
        return [
            {
                'principal': row[0],
                'name': row[1],
                'description': update_image_paths(row[2], f'images/Personnages/{type_folder}/{char_folder}'),
                'image': f'images/Personnages/{type_folder}/{char_folder}/{row[3]}' if row[3] else ''
            }
            for row in self.cursor.fetchall()
        ]

    def get_evolutions(self, char_id, language, type_folder, char_folder, update_image_paths):
        self.cursor.execute("""
            SELECT ce.character_evolutions_evolution_id, ce.character_evolutions_number, ce.character_evolutions_type, ce.character_evolutions_range, cet.character_evolution_translations_description
            FROM character_evolutions ce
            LEFT JOIN character_evolution_translations cet ON cet.character_evolution_translations_character_evolutions_id = ce.character_evolutions_id
            WHERE ce.character_evolutions_characters_id = %s AND (cet.character_evolution_translations_language = %s OR cet.character_evolution_translations_language IS NULL)
        """, (char_id, language))
        return [
            {
                'id': row[0],
                'number': row[1],
                'type': row[2],
                'range': row[3],
                'description': update_image_paths(row[4], f'images/Personnages/{type_folder}/{char_folder}') if row[4] else ''
            }
            for row in self.cursor.fetchall()
        ]

    def get_skills(self, char_id, language, type_folder, char_folder, update_image_paths):
        self.cursor.execute("""
            SELECT s.skills_principal, st.skill_translations_name, st.skill_translations_description, s.skills_image
            FROM skills s
            JOIN skill_translations st ON st.skill_translations_skills_id = s.skills_id
            WHERE s.skills_characters_id = %s AND st.skill_translations_language = %s
        """, (char_id, language))
        return [
            {
                'principal': row[0],
                'name': row[1],
                'description': update_image_paths(row[2], f'images/Personnages/{type_folder}/{char_folder}'),
                'image': f'images/Personnages/{type_folder}/{char_folder}/{row[3]}' if row[3] else ''
            }
            for row in self.cursor.fetchall()
        ]

    def get_weapons(self, char_id, language, type_folder, char_folder, update_image_paths):
        self.cursor.execute("""
            SELECT w.weapons_id, wt.weapon_translations_name, wt.weapon_translations_stats, w.weapons_image
            FROM weapons w
            JOIN weapon_translations wt ON wt.weapon_translations_weapons_id = w.weapons_id
            WHERE w.weapons_characters_id = %s AND wt.weapon_translations_language = %s
        """, (char_id, language))
        weapons = []
        for w_row in self.cursor.fetchall():
            weapon_id, weapon_name, weapon_stats, weapon_image = w_row
            self.cursor.execute("""
                SELECT we.weapon_evolutions_evolution_id, we.weapon_evolutions_number, we.weapon_evolutions_type, we.weapon_evolutions_range, wet.weapon_evolution_translations_description
                FROM weapon_evolutions we
                LEFT JOIN weapon_evolution_translations wet ON wet.weapon_evolution_translations_weapon_evolutions_id = we.weapon_evolutions_id
                WHERE we.weapon_evolutions_weapons_id = %s AND (wet.weapon_evolution_translations_language = %s OR wet.weapon_evolution_translations_language IS NULL)
            """, (weapon_id, language))
            evolutions = [
                {
                    'id': evo[0],
                    'number': evo[1],
                    'type': evo[2],
                    'range': evo[3],
                    'description': update_image_paths(evo[4], f'images/Personnages/{type_folder}/{char_folder}') if evo[4] else ''
                }
                for evo in self.cursor.fetchall()
            ]
            weapons.append({
                'name': weapon_name,
                'stats': update_image_paths(weapon_stats, f'images/Personnages/{type_folder}/{char_folder}') if weapon_stats else '',
                'image': f'images/Personnages/{type_folder}/{char_folder}/{weapon_image}' if weapon_image else '',
                'evolutions': evolutions
            })
        return weapons

    def get_equipment_sets(self, char_id, language):
        self.cursor.execute("""
            SELECT es.equipment_sets_id, es.equipment_sets_name
            FROM equipment_sets es
            WHERE es.equipment_sets_characters_id = %s
        """, (char_id,))
        return self.cursor.fetchall()

    def get_equipment_set_details(self, eq_set_id, eq_set_name, language):
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
                'main_stat': core_row[3],
                'secondary_stat': core_row[4]
            }
            cores.append(core_obj)
        set_piece_count = Counter(artefact_sets)
        return {
            'set_name': eq_set_name,
            'focus_stats': focus_stats,
            'artefacts': artefacts,
            'cores': cores,
            'set_piece_count': dict(set_piece_count)
        }

    def get_panoplies_effects(self, language):
        self.cursor.execute("""
            SELECT p.panoplies_name, psb.panoplie_set_bonus_pieces_required, psbt.panoplie_set_bonus_translations_effect
            FROM panoplies p
            JOIN panoplie_set_bonus psb ON psb.panoplie_set_bonus_panoplies_id = p.panoplies_id
            JOIN panoplie_set_bonus_translations psbt ON psbt.panoplie_set_bonus_translations_panoplie_set_bonus_id = psb.panoplie_set_bonus_id
            WHERE psbt.panoplie_set_bonus_translations_language = %s
        """, (language,))
        return [
            {
                'set_name': row[0],
                'pieces_required': row[1],
                'effect': row[2]
            }
            for row in self.cursor.fetchall()
        ]

    def close(self):
        self.conn.close()
