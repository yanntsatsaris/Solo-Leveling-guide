class SJWShadowsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_shadows(self, sjw_id, language):
        self.cursor.execute("""
            SELECT s.sjw_shadows_id, s.sjw_shadows_image, t.sjw_shadow_translations_name
            FROM sjw_shadows s
            JOIN sjw_shadow_translations t ON t.sjw_shadow_translations_sjw_shadows_id = s.sjw_shadows_id
            WHERE s.sjw_shadows_sjw_id = %s AND t.sjw_shadow_translations_language = %s
        """, (sjw_id, language))
        shadows = []
        for row in self.cursor.fetchall():
            shadow_id = row[0]
            shadow = {
                'id': shadow_id,
                'image': row[1],
                'name': row[2],
                'evolutions': self.get_evolutions(shadow_id, language)
            }
            shadows.append(shadow)
        return shadows

    def get_evolutions(self, shadow_id, language):
        self.cursor.execute("""
            SELECT e.sjw_shadow_evolutions_id, e.sjw_shadow_evolutions_type, t.sjw_shadow_evolution_translations_name, t.sjw_shadow_evolution_translations_description
            FROM sjw_shadow_evolutions e
            JOIN sjw_shadow_evolution_translations t ON t.sjw_shadow_evolution_translations_evolution_id = e.sjw_shadow_evolutions_id
            WHERE e.sjw_shadow_evolutions_sjw_shadows_id = %s AND t.sjw_shadow_evolution_translations_language = %s
        """, (shadow_id, language))
        return [
            {
                'id': row[0],
                'type': row[1],
                'name': row[2],
                'description': row[3]
            }
            for row in self.cursor.fetchall()
        ]