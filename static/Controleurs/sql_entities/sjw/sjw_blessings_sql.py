class SJWBlessingsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_offensive_blessings(self, sjw_id, language):
        self.cursor.execute("""
            SELECT b.sjw_offensive_blessings_id, t.sjw_offensive_blessing_translations_name, t.sjw_offensive_blessing_translations_description, b.sjw_offensive_blessings_image
            FROM sjw_offensive_blessings b
            LEFT JOIN sjw_offensive_blessing_translations t
                ON t.sjw_offensive_blessing_translations_blessing_id = b.sjw_offensive_blessings_id
                AND t.sjw_offensive_blessing_translations_language = %s
            WHERE b.sjw_offensive_blessings_sjw_id = %s
        """, (language, sjw_id))
        return [
            {
                'id': row[0],
                'name': row[1] if row[1] else '',
                'description': row[2] if row[2] else '',
                'image': row[3]
            }
            for row in self.cursor.fetchall()
        ]

    def get_defensive_blessings(self, sjw_id, language):
        self.cursor.execute("""
            SELECT b.sjw_defensive_blessings_id, t.sjw_defensive_blessing_translations_name, t.sjw_defensive_blessing_translations_description, b.sjw_defensive_blessings_image
            FROM sjw_defensive_blessings b
            LEFT JOIN sjw_defensive_blessing_translations t
                ON t.sjw_defensive_blessing_translations_blessing_id = b.sjw_defensive_blessings_id
                AND t.sjw_defensive_blessing_translations_language = %s
            WHERE b.sjw_defensive_blessings_sjw_id = %s
        """, (language, sjw_id))
        return [
            {
                'id': row[0],
                'name': row[1] if row[1] else '',
                'description': row[2] if row[2] else '',
                'image': row[3]
            }
            for row in self.cursor.fetchall()
        ]