from static.Controleurs.ControleurLog import write_log

class WeaponsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_weapons(self, char_id, language, type_folder, char_folder):
        write_log(f"Requête get_weapons pour char_id={char_id}, langue={language}", log_level="DEBUG")
        # Récupère d'abord toutes les armes du personnage
        self.cursor.execute("""
            SELECT weapons_id, weapons_image
            FROM weapons
            WHERE weapons_characters_id = %s
        """, (char_id,))
        weapons = []
        for w_row in self.cursor.fetchall():
            weapon_id, weapon_image = w_row
            # Récupère la traduction pour la langue demandée
            self.cursor.execute("""
                SELECT weapon_translations_name, weapon_translations_stats, weapon_translations_tag
                FROM weapon_translations
                WHERE weapon_translations_weapons_id = %s AND weapon_translations_language = %s
            """, (weapon_id, language))
            trans = self.cursor.fetchone()
            if trans:
                weapon_name, weapon_stats, weapon_tag = trans
            else:
                weapon_name, weapon_stats, weapon_tag = '', '', ''
            # Récupère les évolutions (inchangé)
            self.cursor.execute("""
                SELECT we.weapon_evolutions_id, we.weapon_evolutions_evolution_id, we.weapon_evolutions_number, we.weapon_evolutions_type, we.weapon_evolutions_range, wet.weapon_evolution_translations_description
                FROM weapon_evolutions we
                LEFT JOIN weapon_evolution_translations wet ON wet.weapon_evolution_translations_weapon_evolutions_id = we.weapon_evolutions_id
                WHERE we.weapon_evolutions_weapons_id = %s AND (wet.weapon_evolution_translations_language = %s OR wet.weapon_evolution_translations_language IS NULL)
                ORDER by we.weapon_evolutions_number
            """, (weapon_id, language))
            evolutions = [
                {
                    'id': evo[0],
                    'evolution_id': evo[1],
                    'number': evo[2],
                    'type': evo[3],
                    'range': evo[4],
                    'description': evo[5] if evo[5] else ''
                }
                for evo in self.cursor.fetchall()
            ]
            weapons.append({
                'id': weapon_id,
                'name': weapon_name,
                'stats': weapon_stats if weapon_stats else '',
                'image': f'images/Personnages/{type_folder}/{char_folder}/{weapon_image}' if weapon_image else '',
                'image_name': weapon_image,
                'tag': weapon_tag,
                'evolutions': evolutions
            })
        return weapons

    def get_weapons_full(self, char_id, language):
        self.cursor.execute("""
            SELECT weapons_id, weapons_image
            FROM weapons
            WHERE weapons_characters_id = %s
        """, (char_id,))
        weapons = []
        for w_row in self.cursor.fetchall():
            weapon_id, weapon_image = w_row
            # Récupère la traduction pour la langue demandée
            self.cursor.execute("""
                SELECT weapon_translations_name, weapon_translations_stats, weapon_translations_tag
                FROM weapon_translations
                WHERE weapon_translations_weapons_id = %s AND weapon_translations_language = %s
            """, (weapon_id, language))
            trans = self.cursor.fetchone()
            if trans:
                weapon_name, weapon_stats, weapon_tag = trans
            else:
                weapon_name, weapon_stats, weapon_tag = '', '', ''
            # Récupère les évolutions (inchangé)
            self.cursor.execute("""
                SELECT we.weapon_evolutions_id, we.weapon_evolutions_evolution_id, we.weapon_evolutions_number, we.weapon_evolutions_type, we.weapon_evolutions_range, wet.weapon_evolution_translations_description
                FROM weapon_evolutions we
                LEFT JOIN weapon_evolution_translations wet ON wet.weapon_evolution_translations_weapon_evolutions_id = we.weapon_evolutions_id
                WHERE we.weapon_evolutions_weapons_id = %s AND (wet.weapon_evolution_translations_language = %s OR wet.weapon_evolution_translations_language IS NULL)
                ORDER by we.weapon_evolutions_number
            """, (weapon_id, language))
            evolutions = [
                {
                    'id': evo[0],
                    'evolution_id': evo[1],
                    'number': evo[2],
                    'type': evo[3],
                    'range': evo[4],
                    'description': evo[5] if evo[5] else ''
                }
                for evo in self.cursor.fetchall()
            ]
            weapons.append({
                'id': weapon_id,
                'name': weapon_name,
                'stats': weapon_stats if weapon_stats else '',
                'image_name': weapon_image,
                'tag': weapon_tag,
                'evolutions': evolutions
            })
        return weapons

    def update_weapon(self, wid, name, stats, tag, img, language):
        self.cursor.execute("""
            UPDATE weapons SET weapons_image=%s
            WHERE weapons_id=%s
        """, (img, wid))
        self.cursor.execute("""
            UPDATE weapon_translations SET weapon_translations_name=%s, weapon_translations_stats=%s, weapon_translations_tag=%s
            WHERE weapon_translations_weapons_id=%s AND weapon_translations_language=%s
        """, (name, stats, tag, wid, language))

    def add_weapon(self, char_id, name, stats, tag, img, language):
        # Vérifie si une arme existe déjà pour ce personnage (par nom et image)
        self.cursor.execute("""
            SELECT w.weapons_id FROM weapons w
            JOIN weapon_translations wt ON wt.weapon_translations_weapons_id = w.weapons_id
            WHERE w.weapons_characters_id = %s AND wt.weapon_translations_name = %s
        """, (char_id, name))
        row = self.cursor.fetchone()
        if row:
            wid = row[0]
            # Mets à jour l'image si besoin
            self.cursor.execute("""
                UPDATE weapons SET weapons_image=%s WHERE weapons_id=%s
            """, (img, wid))
            # Vérifie si la traduction existe déjà pour cette langue
            self.cursor.execute("""
                SELECT 1 FROM weapon_translations
                WHERE weapon_translations_weapons_id=%s AND weapon_translations_language=%s
            """, (wid, language))
            if not self.cursor.fetchone():
                self.cursor.execute("""
                    INSERT INTO weapon_translations (weapon_translations_weapons_id, weapon_translations_language, weapon_translations_name, weapon_translations_stats, weapon_translations_tag)
                    VALUES (%s, %s, %s, %s, %s)
                """, (wid, language, name, stats, tag))
            return wid
        else:
            self.cursor.execute("""
                INSERT INTO weapons (weapons_characters_id, weapons_image)
                VALUES (%s, %s) RETURNING weapons_id
            """, (char_id, img))
            wid = self.cursor.fetchone()[0]
            self.cursor.execute("""
                INSERT INTO weapon_translations (weapon_translations_weapons_id, weapon_translations_language, weapon_translations_name, weapon_translations_stats, weapon_translations_tag)
                VALUES (%s, %s, %s, %s, %s)
            """, (wid, language, name, stats, tag))
            return wid

    def delete_weapon(self, wid):
        self.cursor.execute("DELETE FROM weapon_translations WHERE weapon_translations_weapons_id=%s", (wid,))
        self.cursor.execute("DELETE FROM weapons WHERE weapons_id=%s", (wid,))

    def update_weapon_evolution(self, eid, wid, evo_idx, evolution_id, desc, evo_type, evo_range, language):
        self.cursor.execute("""
            UPDATE weapon_evolutions SET weapon_evolutions_evolution_id=%s, weapon_evolutions_number=%s, weapon_evolutions_type=%s, weapon_evolutions_range=%s
            WHERE weapon_evolutions_id=%s
        """, (evolution_id, evo_idx if evo_idx is not None else None, evo_type, evo_range, eid))
        self.cursor.execute("""
            UPDATE weapon_evolution_translations SET weapon_evolution_translations_description=%s
            WHERE weapon_evolution_translations_weapon_evolutions_id=%s AND weapon_evolution_translations_language=%s
        """, (desc, eid, language))

    def add_weapon_evolution(self, wid, evo_idx, evolution_id, desc, evo_type, evo_range, language):
        # Vérifie si une évolution existe déjà pour cette arme avec ce evolution_id
        self.cursor.execute("""
            SELECT weapon_evolutions_id FROM weapon_evolutions
            WHERE weapon_evolutions_weapons_id = %s AND weapon_evolutions_evolution_id = %s
        """, (wid, evolution_id))
        row = self.cursor.fetchone()
        if row:
            eid = row[0]
            # Met à jour la traduction si besoin
            self.cursor.execute("""
                SELECT 1 FROM weapon_evolution_translations
                WHERE weapon_evolution_translations_weapon_evolutions_id = %s AND weapon_evolution_translations_language = %s
            """, (eid, language))
            if not self.cursor.fetchone():
                self.cursor.execute("""
                    INSERT INTO weapon_evolution_translations (weapon_evolution_translations_weapon_evolutions_id, weapon_evolution_translations_language, weapon_evolution_translations_description)
                    VALUES (%s, %s, %s)
                """, (eid, language, desc))
            else:
                self.cursor.execute("""
                    UPDATE weapon_evolution_translations SET weapon_evolution_translations_description=%s
                    WHERE weapon_evolution_translations_weapon_evolutions_id=%s AND weapon_evolution_translations_language=%s
                """, (desc, eid, language))
            # Mets à jour les autres champs si besoin
            self.cursor.execute("""
                UPDATE weapon_evolutions SET weapon_evolutions_number=%s, weapon_evolutions_type=%s, weapon_evolutions_range=%s
                WHERE weapon_evolutions_id=%s
            """, (evo_idx if evo_idx is not None else None, evo_type, evo_range, eid))
            return eid
        else:
            self.cursor.execute("""
                INSERT INTO weapon_evolutions (weapon_evolutions_weapons_id, weapon_evolutions_evolution_id, weapon_evolutions_number, weapon_evolutions_type, weapon_evolutions_range)
                VALUES (%s, %s, %s, %s, %s) RETURNING weapon_evolutions_id
            """, (wid, evolution_id, evo_idx if evo_idx is not None else None, evo_type, evo_range))
            eid = self.cursor.fetchone()[0]
            self.cursor.execute("""
                INSERT INTO weapon_evolution_translations (weapon_evolution_translations_weapon_evolutions_id, weapon_evolution_translations_language, weapon_evolution_translations_description)
                VALUES (%s, %s, %s)
            """, (eid, language, desc))
            return eid