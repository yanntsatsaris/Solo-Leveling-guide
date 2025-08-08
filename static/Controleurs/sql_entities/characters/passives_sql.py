from static.Controleurs.ControleurLog import write_log

class PassivesSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_passives(self, char_id, language, type_folder, char_folder):
        write_log(f"Requête get_passives pour char_id={char_id}, langue={language}", log_level="DEBUG")
        self.cursor.execute("""
            SELECT p.passives_principal, pt.passive_translations_name, pt.passive_translations_description, p.passives_image, pt.passive_translations_tag, p.passives_hidden
            FROM passives p
            JOIN passive_translations pt ON pt.passive_translations_passives_id = p.passives_id
            WHERE p.passives_characters_id = %s AND pt.passive_translations_language = %s
        """, (char_id, language))
        return [
            {
                'id': row[0],  # Ajoute cette ligne (assure-toi que SELECT récupère l'id en premier)
                'principal': row[1],
                'name': row[2],
                'description': row[3],
                'image': f'images/Personnages/{type_folder}/{char_folder}/{row[4]}' if row[4] else '',
                'image_name': row[4],
                'tag': row[5],
                'hidden': row[6]
            }
            for row in self.cursor.fetchall()
        ]

    def get_passives_full(self, char_id, language):
        self.cursor.execute("""
            SELECT p.passives_id, pt.passive_translations_name, pt.passive_translations_description, pt.passive_translations_tag, p.passives_image, p.passives_principal, p.passives_hidden
            FROM passives p
            JOIN passive_translations pt ON pt.passive_translations_passives_id = p.passives_id
            WHERE p.passives_characters_id = %s AND pt.passive_translations_language = %s
        """, (char_id, language))
        return [
            {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'tag': row[3],
                'image_name': row[4],
                'principal': row[5],
                'hidden': row[6]
            }
            for row in self.cursor.fetchall()
        ]

    def update_passive(self, pid, name, desc, tag, img, principal, hidden, language):
        self.cursor.execute("""
            UPDATE passives SET passives_image=%s, passives_principal=%s, passives_hidden=%s
            WHERE passives_id=%s
        """, (img, principal, hidden, pid))
        self.cursor.execute("""
            UPDATE passive_translations SET passive_translations_name=%s, passive_translations_description=%s, passive_translations_tag=%s
            WHERE passive_translations_passives_id=%s AND passive_translations_language=%s
        """, (name, desc, tag, pid, language))

    def add_passive(self, char_id, name, desc, tag, img, principal, hidden, language):
        self.cursor.execute("""
            INSERT INTO passives (passives_characters_id, passives_image, passives_principal, passives_hidden)
            VALUES (%s, %s, %s, %s) RETURNING passives_id
        """, (char_id, img, principal, hidden))
        pid = self.cursor.fetchone()[0]
        self.cursor.execute("""
            INSERT INTO passive_translations (passive_translations_passives_id, passive_translations_language, passive_translations_name, passive_translations_description, passive_translations_tag)
            VALUES (%s, %s, %s, %s, %s)
        """, (pid, language, name, desc, tag))
        return pid

    def delete_passive(self, pid):
        self.cursor.execute("DELETE FROM passive_translations WHERE passive_translations_passives_id=%s", (pid,))
        self.cursor.execute("DELETE FROM passives WHERE passives_id=%s", (pid,))