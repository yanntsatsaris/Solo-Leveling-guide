class SJWSkillsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_skills(self, sjw_id, language):
        self.cursor.execute("""
            SELECT s.sjw_skills_id, s.sjw_skills_image, t.sjw_skill_translations_name, t.sjw_skill_translations_description
            FROM sjw_skills s
            JOIN sjw_skill_translations t ON t.sjw_skill_translations_sjw_skills_id = s.sjw_skills_id
            WHERE s.sjw_skills_sjw_id = %s AND t.sjw_skill_translations_language = %s
        """, (sjw_id, language))
        return [
            {
                'id': row[0],
                'image': row[1],
                'name': row[2],
                'description': row[3]
            }
            for row in self.cursor.fetchall()
        ]