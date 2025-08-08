from static.Controleurs.ControleurLog import write_log

class SkillsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_skills(self, char_id, language, type_folder, char_folder):
        write_log(f"Requête get_skills pour char_id={char_id}, langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT s.skills_principal, st.skill_translations_name, st.skill_translations_description, s.skills_image, st.skill_translations_tag
            FROM skills s
            JOIN skill_translations st ON st.skill_translations_skills_id = s.skills_id
            WHERE s.skills_characters_id = %s AND st.skill_translations_language = %s
        """, (char_id, language))
        return [
            {
                'id': row[0],  # Ajoute l'id
                'principal': row[1],
                'name': row[2],
                'description': row[3],
                'image': f'images/Personnages/{type_folder}/{char_folder}/{row[4]}' if row[4] else '',
                'image_name': row[4],
                'tag': row[5]
            }
            for row in self.cursor.fetchall()
        ]

    def get_skills_full(self, char_id, language):
        self.cursor.execute("""
            SELECT s.skills_id, st.skill_translations_name, st.skill_translations_description, st.skill_translations_tag, s.skills_image, s.skills_principal
            FROM skills s
            JOIN skill_translations st ON st.skill_translations_skills_id = s.skills_id
            WHERE s.skills_characters_id = %s AND st.skill_translations_language = %s
        """, (char_id, language))
        return [
            {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'tag': row[3],
                'image_name': row[4],
                'principal': row[5]
            }
            for row in self.cursor.fetchall()
        ]

    def update_skill(self, sid, name, desc, tag, img, principal, language):
        self.cursor.execute("""
            UPDATE skills SET skills_image=%s, skills_principal=%s
            WHERE skills_id=%s
        """, (img, principal, sid))
        self.cursor.execute("""
            UPDATE skill_translations SET skill_translations_name=%s, skill_translations_description=%s, skill_translations_tag=%s
            WHERE skill_translations_skills_id=%s AND skill_translations_language=%s
        """, (name, desc, tag, sid, language))

    def add_skill(self, char_id, name, desc, tag, img, principal, language):
        self.cursor.execute("""
            INSERT INTO skills (skills_characters_id, skills_image, skills_principal)
            VALUES (%s, %s, %s) RETURNING skills_id
        """, (char_id, img, principal))
        sid = self.cursor.fetchone()[0]
        self.cursor.execute("""
            INSERT INTO skill_translations (skill_translations_skills_id, skill_translations_language, skill_translations_name, skill_translations_description, skill_translations_tag)
            VALUES (%s, %s, %s, %s, %s)
        """, (sid, language, name, desc, tag))
        return sid

    def delete_skill(self, sid):
        self.cursor.execute("DELETE FROM skill_translations WHERE skill_translations_skills_id=%s", (sid,))
        self.cursor.execute("DELETE FROM skills WHERE skills_id=%s", (sid,))