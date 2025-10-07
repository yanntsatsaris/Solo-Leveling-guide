class SJWSkillsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_skills(self, sjw_id, language='FR_fr'):
        self.cursor.execute("""
            SELECT s.sjw_skills_id, s.sjw_skills_type, s.sjw_skills_order, s.sjw_skills_image
            FROM sjw_skills s
            WHERE s.sjw_skills_sjw_id = %s
            ORDER BY s.sjw_skills_order ASC
        """, (sjw_id,))
        skills = []
        for row in self.cursor.fetchall():
            skill_id, skill_type, skill_order, skill_image = row
            if skill_type == 'Skill':
                skill_type_folder = 'Skills'
                skill_order_str = f"{int(skill_order):03d}"  # 3 chiffres, ex: 001
            elif skill_type == 'QTE':
                skill_type_folder = 'QTE'
                skill_order_str = f"{int(skill_order):02d}"  # 2 chiffres, ex: 01
            elif skill_type == 'Ultime':
                skill_type_folder = 'Ultime'
                skill_order_str = f"{int(skill_order):02d}"  # 2 chiffres, ex: 01
            else:
                skill_type_folder = skill_type
                skill_order_str = str(skill_order)

            # Traduction du skill
            self.cursor.execute("""
                SELECT sjw_skill_translations_name, sjw_skill_translations_description
                FROM sjw_skill_translations
                WHERE sjw_skill_translations_sjw_skills_id = %s AND sjw_skill_translations_language = %s
            """, (skill_id, language))
            trans = self.cursor.fetchone()
            name = trans[0] if trans else ''
            description = trans[1] if trans else ''

            # Gems associées
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
                    SELECT sjw_skill_gem_translations_name, sjw_skill_gem_translations_description
                    FROM sjw_skill_gem_translations
                    WHERE sjw_skill_gem_translations_skill_gems_id = %s AND sjw_skill_gem_translations_language = %s
                """, (gem_id, language))
                gem_trans = self.cursor.fetchone()
                gem_name = gem_trans[0] if gem_trans else ''
                gem_description = gem_trans[1] if gem_trans else ''

                # Propriétés de la gem (break uniquement)
                self.cursor.execute("""
                    SELECT sjw_skill_gem_properties_id, sjw_skill_gem_properties_break
                    FROM sjw_skill_gem_properties
                    WHERE sjw_skill_gem_properties_skill_gems_id = %s
                """, (gem_id,))
                prop = self.cursor.fetchone()
                if prop:
                    prop_id, gem_break = prop
                else:
                    gem_break = False

                # Buffs
                self.cursor.execute("""
                    SELECT b.id, b.image, t.name, t.description
                    FROM sjw_skill_gem_buff b
                    LEFT JOIN sjw_skill_gem_buff_translation t ON b.id = t.buff_id AND t.language = %s
                    WHERE b.gem_id = %s
                """, (language, gem_id))
                buffs = []
                for buff_row in self.cursor.fetchall():
                    buff_id, buff_image, buff_name, buff_description = buff_row
                    buffs.append({
                        'id': buff_id,
                        'image': buff_image,
                        'name': buff_name,
                        'description': buff_description
                    })

                # Debuffs
                self.cursor.execute("""
                    SELECT d.id, d.image, t.name, t.description
                    FROM sjw_skill_gem_debuff d
                    LEFT JOIN sjw_skill_gem_debuff_translation t ON d.id = t.debuff_id AND t.language = %s
                    WHERE d.gem_id = %s
                """, (language, gem_id))
                debuffs = []
                for debuff_row in self.cursor.fetchall():
                    debuff_id, debuff_image, debuff_name, debuff_description = debuff_row
                    debuffs.append({
                        'id': debuff_id,
                        'image': f"images/Sung_Jinwoo/{skill_type_folder}/{skill_order_str}_{skill_type}/{debuff_image}",
                        'name': debuff_name,
                        'description': debuff_description
                    })

                gems.append({
                    'id': gem_id,
                    'type': gem_type,
                    'alias': gem_alias,
                    'image_path': f"images/Sung_Jinwoo/{skill_type_folder}/{skill_order_str}_{skill_type}/{gem_image}",
                    'image': gem_image,
                    'name': gem_name,
                    'description': gem_description,
                    'break': gem_break,
                    'buffs': buffs,
                    'debuffs': debuffs
                })

            skills.append({
                'id': skill_id,
                'type': skill_type,
                'order': skill_order_str,
                'image_path': f"images/Sung_Jinwoo/{skill_type_folder}/{skill_order_str}_{skill_type}/{skill_image}",
                'image': skill_image,
                'name': name,
                'description': description,
                'gems': gems
            })
        return skills

    # Création d'un skill
    def add_skill(self, sjw_id, type, order, image):
        self.cursor.execute("""
            SELECT sjw_skills_id FROM sjw_skills
            WHERE sjw_skills_sjw_id = %s AND sjw_skills_type = %s AND sjw_skills_order = %s
        """, (sjw_id, type, order))
        existing = self.cursor.fetchone()
        if existing:
            raise Exception("Un skill avec ce type et cet ordre existe déjà pour ce personnage.")

        self.cursor.execute("""
            SELECT sjw_skills_id FROM sjw_skills
            WHERE sjw_skills_sjw_id = %s AND sjw_skills_image = %s
        """, (sjw_id, image))
        existing_img = self.cursor.fetchone()
        if existing_img:
            raise Exception("Cette image est déjà utilisée pour un autre skill de ce personnage.")

        self.cursor.execute("""
            INSERT INTO sjw_skills (sjw_skills_sjw_id, sjw_skills_type, sjw_skills_order, sjw_skills_image)
            VALUES (%s, %s, %s, %s)
            RETURNING sjw_skills_id
        """, (sjw_id, type, order, image))
        return self.cursor.fetchone()[0]

    def update_skill(self, skill_id, type, order, image):
        self.cursor.execute("""
            UPDATE sjw_skills
            SET sjw_skills_type=%s, sjw_skills_order=%s, sjw_skills_image=%s
            WHERE sjw_skills_id=%s
        """, (type, order, image, skill_id))

    def add_skill_translation(self, skill_id, language, name, description):
        self.cursor.execute("""
            SELECT sjw_skill_translations_id FROM sjw_skill_translations
            WHERE sjw_skill_translations_sjw_skills_id = %s AND sjw_skill_translations_language = %s
        """, (skill_id, language))
        existing = self.cursor.fetchone()
        if existing:
            raise Exception("Une traduction existe déjà pour ce skill et cette langue.")
        self.cursor.execute("""
            INSERT INTO sjw_skill_translations (sjw_skill_translations_sjw_skills_id, sjw_skill_translations_language, sjw_skill_translations_name, sjw_skill_translations_description)
            VALUES (%s, %s, %s, %s)
        """, (skill_id, language, name, description))

    def update_skill_translation(self, skill_id, language, name, description):
        self.cursor.execute("""
            UPDATE sjw_skill_translations
            SET sjw_skill_translations_name=%s, sjw_skill_translations_description=%s
            WHERE sjw_skill_translations_sjw_skills_id=%s AND sjw_skill_translations_language=%s
        """, (name, description, skill_id, language))

    def add_skill_gem(self, skill_id, type, alias, image, order):
        self.cursor.execute("""
            SELECT sjw_skill_gems_id FROM sjw_skill_gems
            WHERE sjw_skill_gems_sjw_skills_id = %s AND sjw_skill_gems_image = %s
        """, (skill_id, image))
        existing_img = self.cursor.fetchone()
        if existing_img:
            raise Exception("Cette image est déjà utilisée pour une autre gem de ce skill.")

        self.cursor.execute("""
            INSERT INTO sjw_skill_gems (sjw_skill_gems_sjw_skills_id, sjw_skill_gems_type, sjw_skill_gems_alias, sjw_skill_gems_image, sjw_skill_gems_order)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING sjw_skill_gems_id
        """, (skill_id, type, alias, image, order))
        return self.cursor.fetchone()[0]

    def update_skill_gem(self, gem_id, type, alias, image, order):
        self.cursor.execute("""
            UPDATE sjw_skill_gems
            SET sjw_skill_gems_type=%s, sjw_skill_gems_alias=%s, sjw_skill_gems_image=%s, sjw_skill_gems_order=%s
            WHERE sjw_skill_gems_id=%s
        """, (type, alias, image, order, gem_id))

    def add_skill_gem_translation(self, gem_id, language, name, description):
        self.cursor.execute("""
            SELECT sjw_skill_gem_translations_id FROM sjw_skill_gem_translations
            WHERE sjw_skill_gem_translations_skill_gems_id = %s AND sjw_skill_gem_translations_language = %s
        """, (gem_id, language))
        existing = self.cursor.fetchone()
        if existing:
            raise Exception("Une traduction existe déjà pour cette gem et cette langue.")
        self.cursor.execute("""
            INSERT INTO sjw_skill_gem_translations (sjw_skill_gem_translations_skill_gems_id, sjw_skill_gem_translations_language, sjw_skill_gem_translations_name, sjw_skill_gem_translations_description)
            VALUES (%s, %s, %s, %s)
        """, (gem_id, language, name, description))

    def update_skill_gem_translation(self, gem_id, language, name, description):
        self.cursor.execute("""
            UPDATE sjw_skill_gem_translations
            SET sjw_skill_gem_translations_name=%s, sjw_skill_gem_translations_description=%s
            WHERE sjw_skill_gem_translations_skill_gems_id=%s AND sjw_skill_gem_translations_language=%s
        """, (name, description, gem_id, language))

    # Propriétés gem (break uniquement)
    def add_skill_gem_properties(self, gem_id, break_value):
        self.cursor.execute("""
            SELECT sjw_skill_gem_properties_id FROM sjw_skill_gem_properties
            WHERE sjw_skill_gem_properties_skill_gems_id = %s
        """, (gem_id,))
        existing = self.cursor.fetchone()
        if existing:
            raise Exception("Des propriétés existent déjà pour cette gem.")
        self.cursor.execute("""
            INSERT INTO sjw_skill_gem_properties (
                sjw_skill_gem_properties_skill_gems_id,
                sjw_skill_gem_properties_break
            ) VALUES (%s, %s)
            RETURNING sjw_skill_gem_properties_id
        """, (gem_id, break_value))
        return self.cursor.fetchone()[0]

    def update_skill_gem_properties(self, gem_id, break_value):
        self.cursor.execute("""
            UPDATE sjw_skill_gem_properties
            SET sjw_skill_gem_properties_break=%s
            WHERE sjw_skill_gem_properties_skill_gems_id=%s
        """, (break_value, gem_id))

    # --- BUFFS ---
    def add_skill_gem_buff(self, gem_id, image):
        # Vérifie que l'image n'est pas déjà utilisée pour un autre buff de cette gem
        self.cursor.execute("""
            SELECT id FROM sjw_skill_gem_buff
            WHERE gem_id = %s AND image = %s
        """, (gem_id, image))
        existing = self.cursor.fetchone()
        if existing:
            raise Exception("Cette image est déjà utilisée pour un autre buff de cette gem.")
        self.cursor.execute("""
            INSERT INTO sjw_skill_gem_buff (gem_id, image)
            VALUES (%s, %s)
            RETURNING id
        """, (gem_id, image))
        return self.cursor.fetchone()[0]

    def update_skill_gem_buff(self, buff_id, image):
        self.cursor.execute("""
            UPDATE sjw_skill_gem_buff SET image=%s WHERE id=%s
        """, (image, buff_id))

    def add_skill_gem_buff_translation(self, buff_id, language, name, description):
        # Vérifie qu'il n'y a pas déjà une traduction pour ce buff et cette langue
        self.cursor.execute("""
            SELECT id FROM sjw_skill_gem_buff_translation
            WHERE buff_id = %s AND language = %s
        """, (buff_id, language))
        existing = self.cursor.fetchone()
        if existing:
            raise Exception("Une traduction existe déjà pour ce buff et cette langue.")
        self.cursor.execute("""
            INSERT INTO sjw_skill_gem_buff_translation (buff_id, language, name, description)
            VALUES (%s, %s, %s, %s)
        """, (buff_id, language, name, description))

    def update_skill_gem_buff_translation(self, buff_id, language, name, description):
        self.cursor.execute("""
            UPDATE sjw_skill_gem_buff_translation
            SET name=%s, description=%s
            WHERE buff_id=%s AND language=%s
        """, (name, description, buff_id, language))

    # --- DEBUFFS ---
    def add_skill_gem_debuff(self, gem_id, image):
        # Vérifie que l'image n'est pas déjà utilisée pour un autre debuff de cette gem
        self.cursor.execute("""
            SELECT id FROM sjw_skill_gem_debuff
            WHERE gem_id = %s AND image = %s
        """, (gem_id, image))
        existing = self.cursor.fetchone()
        if existing:
            raise Exception("Cette image est déjà utilisée pour un autre debuff de cette gem.")
        self.cursor.execute("""
            INSERT INTO sjw_skill_gem_debuff (gem_id, image)
            VALUES (%s, %s)
            RETURNING id
        """, (gem_id, image))
        return self.cursor.fetchone()[0]

    def update_skill_gem_debuff(self, debuff_id, image):
        self.cursor.execute("""
            UPDATE sjw_skill_gem_debuff SET image=%s WHERE id=%s
        """, (image, debuff_id))

    def add_skill_gem_debuff_translation(self, debuff_id, language, name, description):
        # Vérifie qu'il n'y a pas déjà une traduction pour ce debuff et cette langue
        self.cursor.execute("""
            SELECT id FROM sjw_skill_gem_debuff_translation
            WHERE debuff_id = %s AND language = %s
        """, (debuff_id, language))
        existing = self.cursor.fetchone()
        if existing:
            raise Exception("Une traduction existe déjà pour ce debuff et cette langue.")
        self.cursor.execute("""
            INSERT INTO sjw_skill_gem_debuff_translation (debuff_id, language, name, description)
            VALUES (%s, %s, %s, %s)
        """, (debuff_id, language, name, description))

    def update_skill_gem_debuff_translation(self, debuff_id, language, name, description):
        self.cursor.execute("""
            UPDATE sjw_skill_gem_debuff_translation
            SET name=%s, description=%s
            WHERE debuff_id=%s AND language=%s
        """, (name, description, debuff_id, language))