import os

class SJWShadowsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_shadows(self, sjw_id, language, folder=None):
        self.cursor.execute("""
            SELECT s.sjw_shadows_id, s.sjw_shadows_alias, t.sjw_shadow_translations_name, t.sjw_shadow_translations_description
            FROM sjw_shadows s
            JOIN sjw_shadow_translations t ON t.sjw_shadow_translations_sjw_shadows_id = s.sjw_shadows_id
            WHERE s.sjw_shadows_sjw_id = %s AND t.sjw_shadow_translations_language = %s
            ORDER BY s.sjw_shadows_alias ASC
        """, (sjw_id, language))
        shadows = []
        for row in self.cursor.fetchall():
            shadow_id = row[0]
            shadow_alias = row[1]
            shadow_name = row[2]
            # Dossier custom du type Shadow_{name}
            custom_folder = f"Shadow_{shadow_alias}"
            base_dir = os.path.join('static', 'images', folder, 'Shadows', custom_folder) if folder else None
            codex_file = f"{custom_folder}_Codex.webp"
            ombre_file = f"{custom_folder}_Ombre.webp"
            codex_path = f'images/{folder}/Shadows/{custom_folder}/{codex_file}' if base_dir and os.path.isdir(base_dir) else f'images/{folder}/Shadows/{shadow_alias}_Codex.webp'
            image_path = f'images/{folder}/Shadows/{custom_folder}/{ombre_file}' if base_dir and os.path.isdir(base_dir) else f'images/{folder}/Shadows/{shadow_alias}_Ombre.webp'
            shadow = {
                'id': shadow_id,
                'image': image_path,
                'codex': codex_path,
                'alias': shadow_alias,
                'name': shadow_name,
                'description': row[3],
                'evolutions': self.get_evolutions(shadow_id)
            }
            shadows.append(shadow)
        return shadows

    def get_evolutions(self, shadow_id, language):
        self.cursor.execute("""
            SELECT e.sjw_shadow_evolutions_id, e.sjw_shadow_evolutions_type, e.sjw_shadow_evolutions_number, t.sjw_shadow_evolution_translations_description
            FROM sjw_shadow_evolutions e
            LEFT JOIN sjw_shadow_evolution_translations t
              ON t.sjw_shadow_evolution_translations_evolution_id = e.sjw_shadow_evolutions_id
              AND t.sjw_shadow_evolution_translations_language = %s
            WHERE e.sjw_shadow_evolutions_sjw_shadows_id = %s
        """, (language, shadow_id))
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

    def get_shadow_details(self, sjw_id, shadow_alias, language, folder=None):
        self.cursor.execute("""
            SELECT s.sjw_shadows_id, t.sjw_shadow_translations_name, t.sjw_shadow_translations_description
            FROM sjw_shadows s
            JOIN sjw_shadow_translations t ON t.sjw_shadow_translations_sjw_shadows_id = s.sjw_shadows_id
            WHERE s.sjw_shadows_sjw_id = %s AND t.sjw_shadow_translations_language = %s AND s.sjw_shadows_alias = %s
        """, (sjw_id, language, shadow_alias))
        row = self.cursor.fetchone()
        if not row:
            return None
        shadow_id = row[0]
        custom_folder = f"Shadow_{shadow_alias}"
        base_dir = os.path.join('static', 'images', folder, 'Shadows', custom_folder) if folder else None
        codex_file = f"{custom_folder}_Codex.webp"
        ombre_file = f"{custom_folder}_Ombre.webp"
        codex_path = f'images/{folder}/Shadows/{custom_folder}/{codex_file}' if base_dir and os.path.isdir(base_dir) else f'images/{folder}/Shadows/{shadow_alias}_Codex.webp'
        image_path = f'images/{folder}/Shadows/{custom_folder}/{ombre_file}' if base_dir and os.path.isdir(base_dir) else f'images/{folder}/Shadows/{shadow_alias}_Ombre.webp'
        shadow = {
            'id': shadow_id,
            'image': image_path,
            'codex': codex_path,
            'alias': shadow_alias,
            'name': row[1],
            'description': row[2],
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

    def add_shadow(self, sjw_id, alias, name, description, language):
        # Vérifie si un alias existe déjà pour ce SJW
        self.cursor.execute("""
            SELECT 1 FROM sjw_shadows
            WHERE sjw_shadows_sjw_id = %s AND sjw_shadows_alias = %s
        """, (sjw_id, alias))
        if self.cursor.fetchone():
            # Alias déjà utilisé, retourne None ou lève une exception
            return None

        # Ajout de l'ombre
        self.cursor.execute("""
            INSERT INTO sjw_shadows (sjw_shadows_sjw_id, sjw_shadows_alias)
            VALUES (%s, %s)
            RETURNING sjw_shadows_id
        """, (sjw_id, alias))
        shadow_id = self.cursor.fetchone()[0]
        self.cursor.execute("""
            INSERT INTO sjw_shadow_translations (sjw_shadow_translations_sjw_shadows_id, sjw_shadow_translations_language, sjw_shadow_translations_name, sjw_shadow_translations_description)
            VALUES (%s, %s, %s, %s)
            RETURNING sjw_shadow_translations_id
        """, (shadow_id, language, name, description))
        return shadow_id

    def update_shadow(self, shadow_id, alias, name, description, language):
        self.cursor.execute("""
            UPDATE sjw_shadows
            SET sjw_shadows_alias = %s
            WHERE sjw_shadows_id = %s
        """, (alias, shadow_id))
        self.cursor.execute("""
            UPDATE sjw_shadow_translations
            SET sjw_shadow_translations_name = %s,
                sjw_shadow_translations_description = %s
            WHERE sjw_shadow_translations_sjw_shadows_id = %s
              AND sjw_shadow_translations_language = %s
        """, (name, description, shadow_id, language))

    def add_evolution(self, shadow_id, evo_idx, evolution_id, desc, evo_type, evo_range, language):
        self.cursor.execute("""
            SELECT sjw_shadow_evolutions_id FROM sjw_shadow_evolutions
            WHERE sjw_shadow_evolutions_sjw_shadows_id = %s AND sjw_shadow_evolutions_evolution_id = %s
        """, (shadow_id, evolution_id))
        row = self.cursor.fetchone()            
        if row:
            eid = row[0]
            # Met à jour la traduction si besoin
            self.cursor.execute("""
                SELECT 1 FROM sjw_shadow_evolution_translations
                WHERE sjw_shadow_evolution_translations_evolution_id = %s AND sjw_shadow_evolution_translations_language = %s
            """, (eid, language))
            if not self.cursor.fetchone():
                self.cursor.execute("""
                    INSERT INTO sjw_shadow_evolution_translations (sjw_shadow_evolution_translations_evolution_id, sjw_shadow_evolution_translations_language, sjw_shadow_evolution_translations_description)
                    VALUES (%s, %s, %s)
                """, (eid, language, desc))
            else:
                self.cursor.execute("""
                    UPDATE sjw_shadow_evolution_translations SET sjw_shadow_evolution_translations_description=%s
                    WHERE sjw_shadow_evolution_translations_evolution_id=%s AND sjw_shadow_evolution_translations_language=%s
                """, (desc, eid, language))
            # Mets à jour les autres champs si besoin
            self.cursor.execute("""
                UPDATE sjw_shadow_evolutions SET sjw_shadow_evolutions_number=%s, sjw_shadow_evolutions_type=%s, sjw_shadow_evolutions_range=%s
                WHERE sjw_shadow_evolutions_id=%s
            """, (evo_idx if evo_idx is not None else None, evo_type, evo_range, eid))
            return eid
        else:
            self.cursor.execute("""
                INSERT INTO sjw_shadow_evolutions (sjw_shadow_evolutions_sjw_shadows_id, sjw_shadow_evolutions_number, sjw_shadow_evolutions_evolution_id, sjw_shadow_evolutions_type, sjw_shadow_evolutions_range)
                VALUES (%s, %s, %s, %s, %s) RETURNING sjw_shadow_evolutions_id
            """, (shadow_id, evo_idx if evo_idx is not None else None, evolution_id, evo_type, evo_range))
            eid = self.cursor.fetchone()[0]
            self.cursor.execute("""
                INSERT INTO sjw_shadow_evolution_translations (sjw_shadow_evolution_translations_evolution_id, sjw_shadow_evolution_translations_language, sjw_shadow_evolution_translations_description)
                VALUES (%s, %s, %s)
            """, (eid, language, desc))
            return eid

    def update_evolution(self, eid, shadow_id, evo_idx, evolution_id, desc, evo_type, evo_range, language):
        self.cursor.execute("""
            UPDATE sjw_shadow_evolutions SET sjw_shadow_evolutions_evolution_id=%s, sjw_shadow_evolutions_number=%s, sjw_shadow_evolutions_type=%s, sjw_shadow_evolutions_range=%s
            WHERE sjw_shadow_evolutions_id=%s
        """, (evolution_id, evo_idx if evo_idx is not None else None, evo_type, evo_range, eid))
        self.cursor.execute("""
            UPDATE sjw_shadow_evolution_translations SET sjw_shadow_evolution_translations_description=%s
            WHERE sjw_shadow_evolution_translations_evolution_id=%s AND sjw_shadow_evolution_translations_language=%s
        """, (desc, eid, language))