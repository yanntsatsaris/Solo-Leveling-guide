class SJWWeaponsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_weapons(self, sjw_id, language):
        self.cursor.execute("""
            SELECT w.sjw_weapons_id, w.sjw_weapons_image, t.sjw_weapon_translations_name, t.sjw_weapon_translations_description
            FROM sjw_weapons w
            JOIN sjw_weapon_translations t ON t.sjw_weapon_translations_sjw_weapons_id = w.sjw_weapons_id
            WHERE w.sjw_weapons_sjw_id = %s AND t.sjw_weapon_translations_language = %s
        """, (sjw_id, language))
        weapons = []
        for row in self.cursor.fetchall():
            weapon_id = row[0]
            weapon = {
                'id': weapon_id,
                'image': row[1],
                'name': row[2],
                'description': row[3],
                'evolutions': self.get_evolutions(weapon_id, language)
            }
            weapons.append(weapon)
        return weapons

    def get_evolutions(self, weapon_id, language):
        self.cursor.execute("""
            SELECT e.sjw_weapon_evolutions_id, e.sjw_weapon_evolutions_type, t.sjw_weapon_evolution_translations_name, t.sjw_weapon_evolution_translations_description
            FROM sjw_weapon_evolutions e
            JOIN sjw_weapon_evolution_translations t ON t.sjw_weapon_evolution_translations_evolution_id = e.sjw_weapon_evolutions_id
            WHERE e.sjw_weapon_evolutions_sjw_weapons_id = %s AND t.sjw_weapon_evolution_translations_language = %s
        """, (weapon_id, language))
        return [
            {
                'id': row[0],
                'type': row[1],
                'name': row[2],
                'description': row[3]
            }
            for row in self.cursor.fetchall()
        ]