from static.Controleurs.ControleurLog import write_log

class PassivesSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_passives(self, char_id, language, type_folder, char_folder):
        write_log(f"Requête get_passives pour char_id={char_id}, langue={language}", log_level="DEBUG")
        # Récupère d'abord tous les passifs du personnage
        self.cursor.execute("""
            SELECT passives_id, passives_principal, passives_image, passives_hidden, passives_order
            FROM passives
            WHERE passives_characters_id = %s
            ORDER By passives_order
        """, (char_id,))
        passives = []
        for p_row in self.cursor.fetchall():
            passive_id, passive_principal, passive_image, passive_hidden, passive_order = p_row
            # Récupère la traduction pour la langue demandée
            self.cursor.execute("""
                SELECT passive_translations_name, passive_translations_description, passive_translations_tag
                FROM passive_translations
                WHERE passive_translations_passives_id = %s AND passive_translations_language = %s
            """, (passive_id, language))
            trans = self.cursor.fetchone()
            if trans:
                passive_name, passive_desc, passive_tag = trans
            else:
                passive_name, passive_desc, passive_tag = '', '', ''
            passives.append({
                'id': passive_id,
                'principal': passive_principal,
                'name': passive_name,
                'description': passive_desc,
                'image': f'images/Personnages/{type_folder}/{char_folder}/{passive_image}' if passive_image else '',
                'image_name': passive_image,
                'tag': passive_tag,
                'hidden': passive_hidden,
                'order': passive_order
            })
        return passives

    def get_passives_full(self, char_id, language):
        self.cursor.execute("""
            SELECT passives_id, passives_image, passives_principal, passives_hidden, passives_order
            FROM passives
            WHERE passives_characters_id = %s
            ORDER BY passives_order
        """, (char_id,))
        passives = []
        for p_row in self.cursor.fetchall():
            passive_id, passive_image, passive_principal, passive_hidden, passive_order = p_row
            # Récupère la traduction pour la langue demandée
            self.cursor.execute("""
                SELECT passive_translations_name, passive_translations_description, passive_translations_tag
                FROM passive_translations
                WHERE passive_translations_passives_id = %s AND passive_translations_language = %s
            """, (passive_id, language))
            trans = self.cursor.fetchone()
            if trans:
                passive_name, passive_desc, passive_tag = trans
            else:
                passive_name, passive_desc, passive_tag = '', '', ''
            passives.append({
                'id': passive_id,
                'name': passive_name,
                'description': passive_desc,
                'tag': passive_tag,
                'image_name': passive_image,
                'principal': passive_principal,
                'hidden': passive_hidden,
                'order': passive_order
            })
        return passives

    def update_passive(self, pid, name, desc, tag, img, principal, hidden, language, order):
        self.cursor.execute("""
            UPDATE passives SET passives_image=%s, passives_principal=%s, passives_hidden=%s, passives_order=%s
            WHERE passives_id=%s
        """, (img, principal, hidden, order, pid))
        # Vérifie si la traduction existe
        self.cursor.execute(
            "SELECT 1 FROM passive_translations WHERE passive_translations_passives_id = %s AND passive_translations_language = %s",
            (pid, language)
        )
        if not self.cursor.fetchone():
            # Crée la traduction si elle n'existe pas
            self.cursor.execute(
                "INSERT INTO passive_translations (passive_translations_passives_id, passive_translations_language, passive_translations_name, passive_translations_description, passive_translations_tag) VALUES (%s, %s, %s, %s, %s)",
                (pid, language, name, desc, tag)
            )
        else:
            # Sinon, modifie la traduction existante
            self.cursor.execute("""
                UPDATE passive_translations SET passive_translations_name=%s, passive_translations_description=%s, passive_translations_tag=%s
                WHERE passive_translations_passives_id=%s AND passive_translations_language=%s
            """, (name, desc, tag, pid, language))

    def add_passive(self, char_id, name, desc, tag, img, principal, hidden, language, order):
        # Vérifie unicité par image OU par nom si image vide
        if not img:
            self.cursor.execute(
                "SELECT passives_id FROM passives "
                "JOIN passive_translations ON passive_translations_passives_id = passives_id "
                "WHERE passives_characters_id = %s AND passive_translations_name = %s AND passive_translations_language = %s",
                (char_id, name, language)
            )
        else:
            self.cursor.execute(
                "SELECT passives_id FROM passives WHERE passives_characters_id = %s AND passives_image IS NOT DISTINCT FROM %s",
                (char_id, img)
            )
        result = self.cursor.fetchone()
        if result:
            pid = result[0]
            # Vérifie si la traduction existe déjà pour cette langue
            self.cursor.execute(
                "SELECT 1 FROM passive_translations WHERE passive_translations_passives_id = %s AND passive_translations_language = %s",
                (pid, language)
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    "INSERT INTO passive_translations (passive_translations_passives_id, passive_translations_language, passive_translations_name, passive_translations_description, passive_translations_tag) VALUES (%s, %s, %s, %s, %s)",
                    (pid, language, name, desc, tag)
                )
            else:
                self.cursor.execute(
                    "UPDATE passive_translations SET passive_translations_name=%s, passive_translations_description=%s, passive_translations_tag=%s WHERE passive_translations_passives_id=%s AND passive_translations_language=%s",
                    (name, desc, tag, pid, language)
                )
            # Mets à jour l'image, principal et hidden si besoin
            self.cursor.execute(
                "UPDATE passives SET passives_image=%s, passives_principal=%s, passives_hidden=%s, passives_order=%s WHERE passives_id=%s",
                (img, principal, hidden, order, pid)
            )
            return pid
        else:
            self.cursor.execute(
                "INSERT INTO passives (passives_characters_id, passives_image, passives_principal, passives_hidden, passives_order) VALUES (%s, %s, %s, %s, %s) RETURNING passives_id",
                (char_id, img, principal, hidden, order)
            )
            pid = self.cursor.fetchone()[0]
            self.cursor.execute(
                "INSERT INTO passive_translations (passive_translations_passives_id, passive_translations_language, passive_translations_name, passive_translations_description, passive_translations_tag) VALUES (%s, %s, %s, %s, %s)",
                (pid, language, name, desc, tag)
            )
            return pid

    def delete_passive(self, pid):
        self.cursor.execute("DELETE FROM passive_translations WHERE passive_translations_passives_id=%s", (pid,))
        self.cursor.execute("DELETE FROM passives WHERE passives_id=%s", (pid,))