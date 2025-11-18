from static.Controleurs.ControleurLog import write_log
import os

class SJWWeaponsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_weapons(self, sjw_id, language, folder=None):
        self.cursor.execute("""
            SELECT w.sjw_weapons_id, w.sjw_weapons_folder, w.sjw_weapons_alias, w.sjw_weapons_type, w.sjw_weapons_rarity
            FROM sjw_weapons w
            WHERE w.sjw_weapons_sjw_id = %s
            ORDER BY CASE w.sjw_weapons_rarity
                    WHEN 'SSR' THEN 1
                    WHEN 'SR' THEN 2
                    WHEN 'R' THEN 3
                    ELSE 4
                END,
                w.sjw_weapons_type,
                w.sjw_weapons_alias
        """, (sjw_id,))
        weapons = []
        for row in self.cursor.fetchall():
            weapon_id = row[0]
            weapon_folder = row[1]
            weapon_alias = row[2]
            type = row[3]
            rarity = row[4]
            # Récupère la traduction pour la langue demandée
            self.cursor.execute("""
                SELECT t.sjw_weapon_translations_name, t.sjw_weapon_translations_stats
                FROM sjw_weapon_translations t
                WHERE t.sjw_weapon_translations_sjw_weapons_id = %s AND t.sjw_weapon_translations_language = %s
            """, (weapon_id, language))
            trans_row = self.cursor.fetchone()
            weapon_name = trans_row[0] if trans_row else ''
            weapon_stats = trans_row[1] if trans_row else ''
            # Gestion des images (identique à ton code actuel)
            custom_folder = f"{type}_{weapon_alias}" if type and weapon_alias else None
            base_dir_custom = os.path.join('static', 'images', folder, 'Armes', custom_folder) if folder and custom_folder else None
            base_dir_bdd = os.path.join('static', 'images', folder, 'Armes', weapon_folder) if folder and weapon_folder else None
            if base_dir_custom and os.path.isdir(base_dir_custom):
                used_folder = custom_folder
                base_dir = base_dir_custom
            else:
                used_folder = weapon_folder
                base_dir = base_dir_bdd
            webp_image = f"{type}_{weapon_alias}_Arme.webp" if weapon_alias else None
            webp_codex = f"{type}_{weapon_alias}_Codex.webp" if weapon_alias else None
            if base_dir and webp_image and os.path.isfile(os.path.join(base_dir, webp_image)):
                image_path = f'images/{folder}/Armes/{used_folder}/{webp_image}'
            else:
                image_path = f'images/{folder}/Armes/{used_folder}/{row[1]}' if folder and used_folder else row[1]
            if base_dir and webp_codex and os.path.isfile(os.path.join(base_dir, webp_codex)):
                codex_path = f'images/{folder}/Armes/{used_folder}/{webp_codex}'
            else:
                codex_path = f'images/{folder}/Armes/{used_folder}/{row[2]}' if folder and used_folder else row[2]
            weapon = {
                'id': weapon_id,
                'image': image_path,
                'codex': codex_path,
                'folder': weapon_folder,
                'alias': weapon_alias,
                'type': type,
                'rarity': rarity,
                'name': weapon_name,
                'stats': weapon_stats,
                'evolutions': self.get_evolutions(weapon_id, language, folder, weapon_folder)
            }
            weapons.append(weapon)
        return weapons
    
    def get_weapon_details(self, weapon_alias, language, folder=None, weapon_folder=None):
        self.cursor.execute("""
            SELECT w.sjw_weapons_id, w.sjw_weapons_folder, w.sjw_weapons_alias, w.sjw_weapons_type, w.sjw_weapons_rarity
            FROM sjw_weapons w
            WHERE w.sjw_weapons_alias = %s
        """, (weapon_alias,))
        row = self.cursor.fetchone()
        if row:
            weapon_id = row[0]
            weapon_folder = row[1]
            weapon_alias = row[2]
            type = row[3]
            rarity = row[4]
            # Récupère la traduction pour la langue demandée
            self.cursor.execute("""
                SELECT t.sjw_weapon_translations_name, t.sjw_weapon_translations_stats
                FROM sjw_weapon_translations t
                WHERE t.sjw_weapon_translations_sjw_weapons_id = %s AND t.sjw_weapon_translations_language = %s
            """, (weapon_id, language))
            trans_row = self.cursor.fetchone()
            weapon_name = trans_row[0] if trans_row else ''
            weapon_stats = trans_row[1] if trans_row else ''
            # Gestion des images (identique à ton code actuel)
            custom_folder = f"{type}_{weapon_alias}" if type and weapon_alias else None
            base_dir_custom = os.path.join('static', 'images', folder, 'Armes', custom_folder) if folder and custom_folder else None
            base_dir_bdd = os.path.join('static', 'images', folder, 'Armes', weapon_folder) if folder and weapon_folder else None
            if base_dir_custom and os.path.isdir(base_dir_custom):
                used_folder = custom_folder
                base_dir = base_dir_custom
            else:
                used_folder = weapon_folder
                base_dir = base_dir_bdd
            webp_image = f"{type}_{weapon_alias}_Arme.webp" if weapon_alias else None
            webp_codex = f"{type}_{weapon_alias}_Codex.webp" if weapon_alias else None
            if base_dir and webp_image and os.path.isfile(os.path.join(base_dir, webp_image)):
                image_path = f'images/{folder}/Armes/{used_folder}/{webp_image}'
            else:
                image_path = f'images/{folder}/Armes/{used_folder}/{row[1]}' if folder and used_folder else row[1]
            if base_dir and webp_codex and os.path.isfile(os.path.join(base_dir, webp_codex)):
                codex_path = f'images/{folder}/Armes/{used_folder}/{webp_codex}'
            else:
                codex_path = f'images/{folder}/Armes/{used_folder}/{row[2]}' if folder and used_folder else row[2]
            weapon = {
                'id': weapon_id,
                'image': image_path,
                'codex': codex_path,
                'folder': weapon_folder,
                'alias': weapon_alias,
                'type': type,
                'name': weapon_name,
                'stats': weapon_stats,
                'rarity': rarity,
                'evolutions': self.get_evolutions(weapon_id, language, folder, weapon_folder)
            }
            return weapon
        return None

    def get_evolutions(self, weapon_id, language, folder=None, weapon_folder=None):
        self.cursor.execute("""
            SELECT e.sjw_weapon_evolutions_id, e.sjw_weapon_evolutions_number, e.sjw_weapon_evolutions_range, e.sjw_weapon_evolutions_type, e.sjw_weapon_evolutions_evolution_id,
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
                'evolution_id': row[4],
                'description': row[5],
                # Pour une image d'évolution :
                # 'image': f'images/{folder}/Armes/{weapon_folder}/Evolutions/{row[?]}' if folder and weapon_folder else row[?]
            }
            for row in self.cursor.fetchall()
        ]

    def update_weapon(self, wid, alias, name, stats, type, tag, rarity, language):
        self.cursor.execute("""
            UPDATE sjw_weapons SET sjw_weapons_alias=%s, sjw_weapons_type=%s, sjw_weapons_rarity=%s
            WHERE sjw_weapons_id=%s
        """, (alias, type, rarity, wid))
        # Vérifie si la traduction existe
        self.cursor.execute("""
            SELECT 1 FROM sjw_weapon_translations
            WHERE sjw_weapon_translations_sjw_weapons_id=%s AND sjw_weapon_translations_language=%s
        """, (wid, language))
        if not self.cursor.fetchone():
            # Crée la traduction si elle n'existe pas
            self.cursor.execute("""
                INSERT INTO sjw_weapon_translations (sjw_weapon_translations_sjw_weapons_id, sjw_weapon_translations_language, sjw_weapon_translations_name, sjw_weapon_translations_stats, sjw_weapon_translations_tag)
                VALUES (%s, %s, %s, %s, %s)
            """, (wid, language, name, stats, tag))
        else:
            # Sinon, modifie la traduction existante
            self.cursor.execute("""
                UPDATE sjw_weapon_translations SET sjw_weapon_translations_name=%s, sjw_weapon_translations_stats=%s, sjw_weapon_translations_tag=%s
                WHERE sjw_weapon_translations_sjw_weapons_id=%s AND sjw_weapon_translations_language=%s
            """, (name, stats, tag, wid, language))

    def add_weapon(self, sjw_id, alias, name, stats, type, rarity, tag, language):
        # Vérifie si une arme existe déjà pour ce personnage (par nom et image)
        self.cursor.execute("""
            SELECT w.sjw_weapons_id FROM sjw_weapons w
            JOIN sjw_weapon_translations wt ON wt.sjw_weapon_translations_sjw_weapons_id = w.sjw_weapons_id
            WHERE w.sjw_weapons_sjw_id = %s AND w.sjw_weapons_alias = %s
        """, (sjw_id, alias))
        row = self.cursor.fetchone()
        if row:
            wid = row[0]
            # Mets à jour l'image si besoin
            self.cursor.execute("""
                UPDATE sjw_weapons SET sjw_weapons_alias=%s WHERE sjw_weapons_id=%s
            """, (alias, wid))
            # Vérifie si la traduction existe déjà pour cette langue
            self.cursor.execute("""
                SELECT 1 FROM sjw_weapon_translations
                WHERE sjw_weapon_translations_sjw_weapons_id=%s AND sjw_weapon_translations_language=%s
            """, (wid, language))
            if not self.cursor.fetchone():
                self.cursor.execute("""
                    INSERT INTO sjw_weapon_translations (sjw_weapon_translations_sjw_weapons_id, sjw_weapon_translations_language, sjw_weapon_translations_name, sjw_weapon_translations_stats, sjw_weapon_translations_tag)
                    VALUES (%s, %s, %s, %s, %s)
                """, (wid, language, name, stats, tag))
            return wid
        else:
            self.cursor.execute("""
                INSERT INTO sjw_weapons (sjw_weapons_sjw_id, sjw_weapons_alias, sjw_weapons_type, sjw_weapons_rarity)
                VALUES (%s, %s, %s, %s) RETURNING sjw_weapons_id
            """, (sjw_id, alias, type, rarity))
            wid = self.cursor.fetchone()[0]
            self.cursor.execute("""
                INSERT INTO sjw_weapon_translations (sjw_weapon_translations_sjw_weapons_id, sjw_weapon_translations_language, sjw_weapon_translations_name, sjw_weapon_translations_stats, sjw_weapon_translations_tag)
                VALUES (%s, %s, %s, %s, %s)
            """, (wid, language, name, stats, tag))
            return wid
        
    def update_weapon_evolution(self, eid, wid, evo_idx, evolution_id, desc, evo_type, evo_range, language):
        self.cursor.execute("""
            UPDATE sjw_weapon_evolutions SET sjw_weapon_evolutions_evolution_id=%s, sjw_weapon_evolutions_number=%s, sjw_weapon_evolutions_type=%s, sjw_weapon_evolutions_range=%s
            WHERE sjw_weapon_evolutions_id=%s
        """, (evolution_id, evo_idx if evo_idx is not None else None, evo_type, evo_range, eid))
        self.cursor.execute("""
            UPDATE sjw_weapon_evolution_translations SET sjw_weapon_evolution_translations_description=%s
            WHERE sjw_weapon_evolution_translations_weapon_evolutions_id=%s AND sjw_weapon_evolution_translations_language=%s
        """, (desc, eid, language))

    def add_weapon_evolution(self, wid, evo_idx, evolution_id, desc, evo_type, evo_range, language):
        # Vérifie si une évolution existe déjà pour cette arme avec ce evolution_id
        self.cursor.execute("""
            SELECT sjw_weapon_evolutions_id FROM sjw_weapon_evolutions
            WHERE sjw_weapon_evolutions_weapons_id = %s AND sjw_weapon_evolutions_evolution_id = %s
        """, (wid, evolution_id))
        row = self.cursor.fetchone()
        if row:
            eid = row[0]
            # Met à jour la traduction si besoin
            self.cursor.execute("""
                SELECT 1 FROM sjw_weapon_evolution_translations
                WHERE sjw_weapon_evolution_translations_weapon_evolutions_id = %s AND sjw_weapon_evolution_translations_language = %s
            """, (eid, language))
            if not self.cursor.fetchone():
                self.cursor.execute("""
                    INSERT INTO sjw_weapon_evolution_translations (sjw_weapon_evolution_translations_weapon_evolutions_id, sjw_weapon_evolution_translations_language, sjw_weapon_evolution_translations_description)
                    VALUES (%s, %s, %s)
                """, (eid, language, desc))
            else:
                self.cursor.execute("""
                    UPDATE sjw_weapon_evolution_translations SET sjw_weapon_evolution_translations_description=%s
                    WHERE sjw_weapon_evolution_translations_weapon_evolutions_id=%s AND sjw_weapon_evolution_translations_language=%s
                """, (desc, eid, language))
            # Mets à jour les autres champs si besoin
            self.cursor.execute("""
                UPDATE sjw_weapon_evolutions SET sjw_weapon_evolutions_number=%s, sjw_weapon_evolutions_type=%s, sjw_weapon_evolutions_range=%s
                WHERE sjw_weapon_evolutions_id=%s
            """, (evo_idx if evo_idx is not None else None, evo_type, evo_range, eid))
            return eid
        else:
            self.cursor.execute("""
                INSERT INTO sjw_weapon_evolutions (sjw_weapon_evolutions_weapons_id, sjw_weapon_evolutions_evolution_id, sjw_weapon_evolutions_number, sjw_weapon_evolutions_type, sjw_weapon_evolutions_range)
                VALUES (%s, %s, %s, %s, %s) RETURNING sjw_weapon_evolutions_id
            """, (wid, evolution_id, evo_idx if evo_idx is not None else None, evo_type, evo_range))
            eid = self.cursor.fetchone()[0]
            self.cursor.execute("""
                INSERT INTO sjw_weapon_evolution_translations (sjw_weapon_evolution_translations_weapon_evolutions_id, sjw_weapon_evolution_translations_language, sjw_weapon_evolution_translations_description)
                VALUES (%s, %s, %s)
            """, (eid, language, desc))
            return eid