class SJWSkillsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_skills(self, sjw_id, language='FR_fr'):
        # Récupère tous les skills du SJW, triés par ordre d'affichage
        self.cursor.execute("""
            SELECT s.sjw_skills_id, s.sjw_skills_type, s.sjw_skills_order, s.sjw_skills_image
            FROM sjw_skills s
            WHERE s.sjw_skills_sjw_id = %s
            ORDER BY s.sjw_skills_order ASC
        """, (sjw_id,))
        skills = []
        for row in self.cursor.fetchall():
            skill_id, skill_type, skill_order, skill_image = row

            # Récupère la traduction du skill
            self.cursor.execute("""
                SELECT sjw_skill_translations_name, sjw_skill_translations_description
                FROM sjw_skill_translations
                WHERE sjw_skill_translations_sjw_skills_id = %s AND sjw_skill_translations_language = %s
            """, (skill_id, language))
            trans = self.cursor.fetchone()
            name = trans[0] if trans else ''
            description = trans[1] if trans else ''

            # Récupère les gems associées à ce skill
            self.cursor.execute("""
                SELECT g.sjw_skill_gems_id, g.sjw_skill_gems_type, g.sjw_skill_gems_alias, g.sjw_skill_gems_image
                FROM sjw_skill_gems g
                WHERE g.sjw_skill_gems_sjw_skills_id = %s
            """, (skill_id,))
            gems = []
            for gem_row in self.cursor.fetchall():
                gem_id, gem_type, gem_alias, gem_image = gem_row

                # Traduction de la gem
                self.cursor.execute("""
                    SELECT sjw_skill_gem_translations_name
                    FROM sjw_skill_gem_translations
                    WHERE sjw_skill_gem_translations_skill_gems_id = %s AND sjw_skill_gem_translations_language = %s
                """, (gem_id, language))
                gem_trans = self.cursor.fetchone()
                gem_name = gem_trans[0] if gem_trans else ''

                # Propriétés de la gem
                self.cursor.execute("""
                    SELECT sjw_skill_gem_properties_break, sjw_skill_gem_properties_buff, sjw_skill_gem_properties_debuff
                    FROM sjw_skill_gem_properties
                    WHERE sjw_skill_gem_properties_skill_gems_id = %s
                """, (gem_id,))
                prop = self.cursor.fetchone()
                gem_break = prop[0] if prop else False
                gem_buff = prop[1] if prop else None
                gem_debuff = prop[2] if prop else None

                gems.append({
                    'id': gem_id,
                    'type': gem_type,
                    'alias': gem_alias,
                    'image': gem_image,
                    'name': gem_name,
                    'break': gem_break,
                    'buff': gem_buff,
                    'debuff': gem_debuff
                })

            skills.append({
                'id': skill_id,
                'type': skill_type,
                'order': skill_order,
                'image': skill_image,
                'name': name,
                'description': description,
                'gems': gems
            })
        return skills