class SJWBlessingsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_offensive_blessings(self, sjw_id):
        self.cursor.execute("""
            SELECT sjw_offensive_blessings_id, sjw_offensive_blessings_name, sjw_offensive_blessings_description, sjw_offensive_blessings_image
            FROM sjw_offensive_blessings
            WHERE sjw_offensive_blessings_sjw_id = %s
        """, (sjw_id,))
        return [
            {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'image': row[3]
            }
            for row in self.cursor.fetchall()
        ]

    def get_defensive_blessings(self, sjw_id):
        self.cursor.execute("""
            SELECT sjw_defensive_blessings_id, sjw_defensive_blessings_name, sjw_defensive_blessings_description, sjw_defensive_blessings_image
            FROM sjw_defensive_blessings
            WHERE sjw_defensive_blessings_sjw_id = %s
        """, (sjw_id,))
        return [
            {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'image': row[3]
            }
            for row in self.cursor.fetchall()
        ]