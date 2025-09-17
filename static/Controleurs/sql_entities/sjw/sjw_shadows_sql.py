import os

class SJWShadowsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_shadows(self, sjw_id, language, folder=None):
        self.cursor.execute("""
            SELECT s.sjw_shadows_id, s.sjw_shadows_image, t.sjw_shadow_translations_name, t.sjw_shadow_translations_description
            FROM sjw_shadows s
            JOIN sjw_shadow_translations t ON t.sjw_shadow_translations_sjw_shadows_id = s.sjw_shadows_id
            WHERE s.sjw_shadows_sjw_id = %s AND t.sjw_shadow_translations_language = %s
        """, (sjw_id, language))
        shadows = []
        for row in self.cursor.fetchall():
            shadow_id = row[0]
            shadow_name = row[2]
            # Dossier custom du type Shadow_{name}
            custom_folder = f"Shadow_{shadow_name}"
            base_dir = os.path.join('static', 'images', folder, 'Shadows', custom_folder) if folder else None
            codex_file = f"{custom_folder}_Codex.webp"
            ombre_file = f"{custom_folder}_Ombre.webp"
            if base_dir and os.path.isdir(base_dir):
                codex_path = f'images/{folder}/Shadows/{custom_folder}/{codex_file}'
                image_path = f'images/{folder}/Shadows/{custom_folder}/{ombre_file}'
            else:
                codex_path = f'images/{folder}/Shadows/{row[1]}'
                image_path = f'images/{folder}/Shadows/{row[1]}'
            shadow = {
                'id': shadow_id,
                'image': image_path,
                'codex': codex_path,
                'name': shadow_name,
                'description': row[3],
                'evolutions': self.get_evolutions(shadow_id)
            }
            shadows.append(shadow)
        return shadows

    def get_evolutions(self, shadow_id):
        self.cursor.execute("""
            SELECT sjw_shadow_evolutions_id, sjw_shadow_evolutions_type, sjw_shadow_evolutions_number, sjw_shadow_evolutions_description
            FROM sjw_shadow_evolutions
            WHERE sjw_shadow_evolutions_sjw_shadows_id = %s
        """, (shadow_id,))
        return [
            {
                'id': row[0],
                'type': row[1],
                'number': row[2],
                'description': row[3]
            }
            for row in self.cursor.fetchall()
        ]

    def get_weapon_for_shadow(self, shadow_id, language, folder=None):
        self.cursor.execute("""
            SELECT w.sjw_shadow_weapons_id, w.sjw_shadow_weapons_image, t.sjw_shadow_weapon_translations_name, t.sjw_shadow_weapon_translations_stats
            FROM sjw_shadow_weapons w
            JOIN sjw_shadow_weapon_translations t ON t.sjw_shadow_weapon_translations_sjw_shadow_weapons_id = w.sjw_shadow_weapons_id
            WHERE w.sjw_shadow_weapons_sjw_shadows_id = %s AND t.sjw_shadow_weapon_translations_language = %s
        """, (shadow_id, language))
        row = self.cursor.fetchone()
        if not row:
            return None
        weapon_id = row[0]
        weapon = {
            'id': weapon_id,
            'image': f'images/{folder}/Weapons/{row[1]}' if folder else row[1],
            'name': row[2],
            'stats': row[3],
            'evolutions': self.get_weapon_evolutions(weapon_id)
        }
        return weapon

    def get_weapon_evolutions(self, weapon_id):
        self.cursor.execute("""
            SELECT sjw_weapon_evolutions_id, sjw_weapon_evolutions_description
            FROM sjw_weapon_evolutions
            WHERE sjw_weapon_evolutions_sjw_weapons_id = %s
            ORDER BY sjw_weapon_evolutions_id ASC
        """, (weapon_id,))
        return [
            {
                'id': row[0],
                'description': row[1]
            }
            for row in self.cursor.fetchall()
        ]

    def get_shadow_details(self, sjw_id, shadow_name, language, folder=None):
        self.cursor.execute("""
            SELECT s.sjw_shadows_id, s.sjw_shadows_image, t.sjw_shadow_translations_name, t.sjw_shadow_translations_description
            FROM sjw_shadows s
            JOIN sjw_shadow_translations t ON t.sjw_shadow_translations_sjw_shadows_id = s.sjw_shadows_id
            WHERE s.sjw_shadows_sjw_id = %s AND t.sjw_shadow_translations_language = %s AND t.sjw_shadow_translations_name = %s
        """, (sjw_id, language, shadow_name))
        row = self.cursor.fetchone()
        if not row:
            return None
        shadow_id = row[0]
        custom_folder = f"Shadow_{shadow_name}"
        base_dir = os.path.join('static', 'images', folder, 'Shadows', custom_folder) if folder else None
        codex_file = f"{custom_folder}_Codex.webp"
        ombre_file = f"{custom_folder}_Ombre.webp"
        if base_dir and os.path.isdir(base_dir):
            codex_path = f'images/{folder}/Shadows/{custom_folder}/{codex_file}'
            image_path = f'images/{folder}/Shadows/{custom_folder}/{ombre_file}'
        else:
            codex_path = f'images/{folder}/Shadows/{row[1]}'
            image_path = f'images/{folder}/Shadows/{row[1]}'
        shadow = {
            'id': shadow_id,
            'image': image_path,
            'codex': codex_path,
            'name': row[2],
            'description': row[3],
            'evolutions': self.get_evolutions(shadow_id),
            'skills': self.get_skills(shadow_id, language, folder),
            'weapon': self.get_weapon_for_shadow(shadow_id, language, folder),
            'authority_passives': self.get_authority_passives(shadow_id, language)
        }
        return shadow

    def get_skills(self, shadow_id, language, folder=None):
        self.cursor.execute("""
            SELECT s.sjw_shadow_skills_id, s.sjw_shadow_skills_principal, s.sjw_shadow_skills_image, s.sjw_shadow_skills_tag, s.sjw_shadow_skills_order,
                   t.sjw_shadow_skill_translations_name, t.sjw_shadow_skill_translations_description, t.sjw_shadow_skill_translations_tag
            FROM sjw_shadow_skills s
            JOIN sjw_shadow_skill_translations t ON t.sjw_shadow_skill_translations_sjw_shadow_skills_id = s.sjw_shadow_skills_id
            WHERE s.sjw_shadow_skills_sjw_shadows_id = %s AND t.sjw_shadow_skill_translations_language = %s
            ORDER BY s.sjw_shadow_skills_order ASC, s.sjw_shadow_skills_id ASC
        """, (shadow_id, language))
        return [
            {
                'id': row[0],
                'principal': row[1],
                'image': f'images/{folder}/Shadows/Skills/{row[2]}' if folder else row[2],
                'tag': row[3],
                'order': row[4],
                'name': row[5],
                'description': row[6],
                'translation_tag': row[7]
            }
            for row in self.cursor.fetchall()
        ]

    def get_authority_passives(self, shadow_id, language):
        self.cursor.execute("""
            SELECT ap.sjw_shadow_authority_passives_id,
                   t.sjw_shadow_authority_passive_translations_name,
                   t.sjw_shadow_authority_passive_translations_description
            FROM sjw_shadow_authority_passives ap
            JOIN sjw_shadow_authority_passive_translations t
              ON t.sjw_shadow_authority_passive_translations_authority_passive_id = ap.sjw_shadow_authority_passives_id
            WHERE ap.sjw_shadow_authority_passives_sjw_shadows_id = %s
              AND t.sjw_shadow_authority_passive_translations_language = %s
        """, (shadow_id, language))
        return [
            {
                'id': row[0],
                'name': row[1],
                'description': row[2]
            }
            for row in self.cursor.fetchall()
        ]