from static.Controleurs.ControleurLog import write_log

class WeaponsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_weapons(self, char_id, language, type_folder, char_folder):
        write_log(f"Requête get_weapons pour char_id={char_id}, langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT w.weapons_id, wt.weapon_translations_name, wt.weapon_translations_stats, w.weapons_image, wt.weapon_translations_tag
            FROM weapons w
            JOIN weapon_translations wt ON wt.weapon_translations_weapons_id = w.weapons_id
            WHERE w.weapons_characters_id = %s AND wt.weapon_translations_language = %s
        """, (char_id, language))
        weapons = []
        for w_row in self.cursor.fetchall():
            weapon_id, weapon_name, weapon_stats, weapon_image, weapon_tag = w_row
            self.cursor.execute("""
                SELECT we.weapon_evolutions_evolution_id, we.weapon_evolutions_number, we.weapon_evolutions_type, we.weapon_evolutions_range, wet.weapon_evolution_translations_description
                FROM weapon_evolutions we
                LEFT JOIN weapon_evolution_translations wet ON wet.weapon_evolution_translations_weapon_evolutions_id = we.weapon_evolutions_id
                WHERE we.weapon_evolutions_weapons_id = %s AND (wet.weapon_evolution_translations_language = %s OR wet.weapon_evolution_translations_language IS NULL)
            """, (weapon_id, language))
            evolutions = [
                {
                    'id': evo[0],
                    'number': evo[1],
                    'type': evo[2],
                    'range': evo[3],
                    'description': evo[4] if evo[4] else ''
                }
                for evo in self.cursor.fetchall()
            ]
            weapons.append({
                'name': weapon_name,
                'stats': weapon_stats if weapon_stats else '',
                'image': f'images/Personnages/{type_folder}/{char_folder}/{weapon_image}' if weapon_image else '',
                'image_name': weapon_image,
                'tag': weapon_tag,  # Ajout du tag de l'arme
                'evolutions': evolutions
            })
        return weapons