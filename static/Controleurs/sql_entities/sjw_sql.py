class SJWSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_sjw(self, language, alias="SJW"):
        self.cursor.execute("""
            SELECT s.sjw_id, s.sjw_alias, s.sjw_folder,
                   t.sjw_translations_name, t.sjw_translations_description
            FROM sjw s
            JOIN sjw_translations t ON t.sjw_translations_sjw_id = s.sjw_id
            WHERE s.sjw_alias = %s AND t.sjw_translations_language = %s
        """, (alias, language))
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            'id': row[0],
            'alias': row[1],
            'folder': row[2],
            'name': row[3],
            'description': row[4]
        }