from static.Controleurs.ControleurLog import write_log

class SJWWeaponsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_weapons(self, sjw_id, language, folder=None):
        self.cursor.execute("""
            SELECT w.sjw_weapons_id, w.sjw_weapons_image, w.sjw_weapons_codex, w.sjw_weapons_folder, w.sjw_weapons_alias, w.sjw_weapons_type, t.sjw_weapon_translations_name, t.sjw_weapon_translations_stats
            FROM sjw_weapons w
            JOIN sjw_weapon_translations t ON t.sjw_weapon_translations_sjw_weapons_id = w.sjw_weapons_id
            WHERE w.sjw_weapons_sjw_id = %s AND t.sjw_weapon_translations_language = %s
            ORDER by t.sjw_weapon_translations_name
        """, (sjw_id, language))
        weapons = []
        for row in self.cursor.fetchall():
            weapon_id = row[0]
            weapon_folder = row[3]
            weapon_alias = row[4]
            type = row[5]
            # Si alias et dossier existent, on tente le .webp
            if folder and weapon_folder and weapon_alias:
                image_path = f'images/{folder}/Armes/{weapon_folder}/{type}_{weapon_alias}_Arme.webp'
                codex_path = f'images/{folder}/Armes/{weapon_folder}/{type}_{weapon_alias}_Codex.webp'
            else:
                image_path = f'images/{folder}/Armes/{weapon_folder}/{row[1]}' if folder and weapon_folder else row[1]
                codex_path = f'images/{folder}/Armes/{weapon_folder}/{row[2]}' if folder and weapon_folder else row[2]
            weapon = {
                'id': weapon_id,
                'image': image_path,
                'codex': codex_path,
                'folder': weapon_folder,
                'alias': weapon_alias,
                'type': type,
                'name': row[6],
                'stats': row[7],
                'evolutions': self.get_evolutions(weapon_id, language, folder, weapon_folder)
            }
            weapons.append(weapon)
        return weapons
    
    def get_weapon_details(self, weapon_alias, language, folder=None, weapon_folder=None):
        self.cursor.execute("""
            SELECT w.sjw_weapons_id, w.sjw_weapons_image, w.sjw_weapons_codex, w.sjw_weapons_folder, w.sjw_weapons_alias, w.sjw_weapons_type, t.sjw_weapon_translations_name, t.sjw_weapon_translations_stats
            FROM sjw_weapons w
            JOIN sjw_weapon_translations t ON t.sjw_weapon_translations_sjw_weapons_id = w.sjw_weapons_id
            WHERE w.sjw_weapons_alias = %s AND t.sjw_weapon_translations_language = %s
        """, (weapon_alias, language))
        row = self.cursor.fetchone()
        if row:
            weapon_id = row[0]
            weapon_folder = row[3]
            weapon_alias = row[4]
            type = row[5]
            # Si alias et dossier existent, on tente le .webp
            if folder and weapon_folder and weapon_alias:
                image_path = f'images/{folder}/Armes/{weapon_folder}/{type}_{weapon_alias}_Arme.webp'
                codex_path = f'images/{folder}/Armes/{weapon_folder}/{type}_{weapon_alias}_Codex.webp'
            else:
                image_path = f'images/{folder}/Armes/{weapon_folder}/{row[1]}' if folder and weapon_folder else row[1]
                codex_path = f'images/{folder}/Armes/{weapon_folder}/{row[2]}' if folder and weapon_folder else row[2]
            weapon = {
                'id': row[0],
                'image': image_path,
                'codex': codex_path,
                'folder': weapon_folder,
                'alias': weapon_alias,
                'type': type,
                'name': row[6],
                'stats': row[7],
                'evolutions': self.get_evolutions(weapon_id, language, folder, weapon_folder)
            }
            return weapon
        return None

    def get_evolutions(self, weapon_id, language, folder=None, weapon_folder=None):
        self.cursor.execute("""
            SELECT e.sjw_weapon_evolutions_id, e.sjw_weapon_evolutions_number, e.sjw_weapon_evolutions_range, e.sjw_weapon_evolutions_type,
                   t.sjw_weapon_evolution_translations_description
            FROM sjw_weapon_evolutions e
            LEFT JOIN sjw_weapon_evolution_translations t
                ON t.sjw_weapon_evolution_translations_sjw_weapon_evolutions_id = e.sjw_weapon_evolutions_id
                AND t.sjw_weapon_evolution_translations_language = %s
            WHERE e.sjw_weapon_evolutions_sjw_weapons_id = %s
        """, (language, weapon_id))
        return [
            {
                'id': row[0],
                'number': row[1],
                'range': row[2],
                'type': row[3],
                'description': row[4],
                # Pour une image d'évolution :
                # 'image': f'images/{folder}/Armes/{weapon_folder}/Evolutions/{row[?]}' if folder and weapon_folder else row[?]
            }
            for row in self.cursor.fetchall()
        ]