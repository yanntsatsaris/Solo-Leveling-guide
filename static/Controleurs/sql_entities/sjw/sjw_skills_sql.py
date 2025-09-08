class SJWSkillsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_skills(self, sjw_id, language=None):
        self.cursor.execute("""
            SELECT sjw_skills_id, sjw_skills_name, sjw_skills_type, sjw_skills_description, sjw_skills_image
            FROM sjw_skills
            WHERE sjw_skills_sjw_id = %s
        """, (sjw_id,))
        return [
            {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'description': row[3],
                'image': row[4]
            }
            for row in self.cursor.fetchall()
        ]