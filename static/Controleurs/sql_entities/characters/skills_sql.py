from static.Controleurs.ControleurLog import write_log

class SkillsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_skills(self, char_id, language, type_folder, char_folder):
        write_log(f"Requête get_skills pour char_id={char_id}, langue={language}", log_level="DEBUG")
        # Récupère d'abord tous les skills du personnage
        self.cursor.execute("""
            SELECT skills_id, skills_principal, skills_image, skills_order
            FROM skills
            WHERE skills_characters_id = %s
            ORDER By skills_order
        """, (char_id,))
        skills = []
        for s_row in self.cursor.fetchall():
            skill_id, skill_principal, skill_image, skill_order = s_row
            # Récupère la traduction pour la langue demandée
            self.cursor.execute("""
                SELECT skill_translations_name, skill_translations_description, skill_translations_tag
                FROM skill_translations
                WHERE skill_translations_skills_id = %s AND skill_translations_language = %s
            """, (skill_id, language))
            trans = self.cursor.fetchone()
            if trans:
                skill_name, skill_desc, skill_tag = trans
            else:
                skill_name, skill_desc, skill_tag = '', '', ''
            skills.append({
                'id': skill_id,
                'principal': skill_principal,
                'name': skill_name,
                'description': skill_desc,
                'image': f'images/Personnages/{type_folder}/{char_folder}/{skill_image}' if skill_image else '',
                'image_name': skill_image,
                'tag': skill_tag,
                'order': skill_order
            })
        return skills

    def get_skills_full(self, char_id, language):
        self.cursor.execute("""
            SELECT skills_id, skills_image, skills_principal, skills_order
            FROM skills
            WHERE skills_characters_id = %s
            ORDER BY skills_order
        """, (char_id,))
        skills = []
        for s_row in self.cursor.fetchall():
            skill_id, skill_image, skill_principal, skill_order = s_row
            # Récupère la traduction pour la langue demandée
            self.cursor.execute("""
                SELECT skill_translations_name, skill_translations_description, skill_translations_tag
                FROM skill_translations
                WHERE skill_translations_skills_id = %s AND skill_translations_language = %s
            """, (skill_id, language))
            trans = self.cursor.fetchone()
            if trans:
                skill_name, skill_desc, skill_tag = trans
            else:
                skill_name, skill_desc, skill_tag = '', '', ''
            skills.append({
                'id': skill_id,
                'name': skill_name,
                'description': skill_desc,
                'tag': skill_tag,
                'image_name': skill_image,
                'principal': skill_principal,
                'order': skill_order
            })
        return skills

    def update_skill(self, sid, name, desc, tag, img, principal, language, order):
        self.cursor.execute("""
            UPDATE skills SET skills_image=%s, skills_principal=%s, skills_order=%s
            WHERE skills_id=%s
        """, (img, principal, order, sid))
        self.cursor.execute("""
            UPDATE skill_translations SET skill_translations_name=%s, skill_translations_description=%s, skill_translations_tag=%s
            WHERE skill_translations_skills_id=%s AND skill_translations_language=%s
        """, (name, desc, tag, sid, language))

    def add_skill(self, char_id, name, desc, tag, img, principal, language, order):
        # Vérifie unicité par image OU par nom si image vide
        if not img:
            self.cursor.execute(
                "SELECT skills_id FROM skills "
                "JOIN skill_translations ON skill_translations_skills_id = skills_id "
                "WHERE skills_characters_id = %s AND skill_translations_name = %s AND skill_translations_language = %s",
                (char_id, name, language)
            )
        else:
            self.cursor.execute(
                "SELECT skills_id FROM skills WHERE skills_characters_id = %s AND skills_image IS NOT DISTINCT FROM %s",
                (char_id, img)
            )
        result = self.cursor.fetchone()
        if result:
            sid = result[0]
            # Vérifie si la traduction existe déjà pour cette langue
            self.cursor.execute(
                "SELECT 1 FROM skill_translations WHERE skill_translations_skills_id = %s AND skill_translations_language = %s",
                (sid, language)
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    "INSERT INTO skill_translations (skill_translations_skills_id, skill_translations_language, skill_translations_name, skill_translations_description, skill_translations_tag) VALUES (%s, %s, %s, %s, %s)",
                    (sid, language, name, desc, tag)
                )
            else:
                self.cursor.execute(
                    "UPDATE skill_translations SET skill_translations_name=%s, skill_translations_description=%s, skill_translations_tag=%s WHERE skill_translations_skills_id=%s AND skill_translations_language=%s",
                    (name, desc, tag, sid, language)
                )
            # Mets à jour l'image et principal si besoin
            self.cursor.execute(
                "UPDATE skills SET skills_image=%s, skills_principal=%s, skills_order=%s WHERE skills_id=%s",
                (img, principal, order, sid)
            )
            return sid
        else:
            self.cursor.execute(
                "INSERT INTO skills (skills_characters_id, skills_image, skills_principal, skills_order) VALUES (%s, %s, %s, %s) RETURNING skills_id",
                (char_id, img, principal, order)
            )
            sid = self.cursor.fetchone()[0]
            self.cursor.execute(
                "INSERT INTO skill_translations (skill_translations_skills_id, skill_translations_language, skill_translations_name, skill_translations_description, skill_translations_tag) VALUES (%s, %s, %s, %s, %s)",
                (sid, language, name, desc, tag)
            )
            return sid

    def delete_skill(self, sid):
        self.cursor.execute("DELETE FROM skill_translations WHERE skill_translations_skills_id=%s", (sid,))
        self.cursor.execute("DELETE FROM skills WHERE skills_id=%s", (sid,))