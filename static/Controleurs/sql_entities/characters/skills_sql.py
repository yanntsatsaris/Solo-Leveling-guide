from static.Controleurs.ControleurLog import write_log

class SkillsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_skills(self, char_id, language, type_folder, char_folder, update_image_paths):
        write_log(f"Requête get_skills pour char_id={char_id}, langue={language}", log_level="DEBUG")
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