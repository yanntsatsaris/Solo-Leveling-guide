class SJWGemsSql:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_gems(self, sjw_id):
        self.cursor.execute("""
            SELECT sjw_gems_color, sjw_gems_stat
            FROM sjw_gems
            WHERE sjw_gems_sjw_id = %s
        """, (sjw_id,))
        gems = {row[0]: row[1] for row in self.cursor.fetchall()}
        # Toujours retourner les 5 couleurs, même si vides
        for color in ['red', 'blue', 'green', 'yellow', 'purple']:
            if color not in gems:
                gems[color] = ''
        return gems

    def update_gem(self, sjw_id, color, stat):
        self.cursor.execute("""
            UPDATE sjw_gems
            SET sjw_gems_stat = %s
            WHERE sjw_gems_sjw_id = %s AND sjw_gems_color = %s
        """, (stat, sjw_id, color))

    def add_gem(self, sjw_id, color, stat):
        self.cursor.execute("""
            SELECT 1 FROM sjw_gems WHERE sjw_gems_sjw_id = %s AND sjw_gems_color = %s
        """, (sjw_id, color))
        if self.cursor.fetchone():
            self.update_gem(sjw_id, color, stat)
        else:
            self.cursor.execute("""
                INSERT INTO sjw_gems (sjw_gems_sjw_id, sjw_gems_color, sjw_gems_stat)
                VALUES (%s, %s, %s)
            """, (sjw_id, color, stat))

    def delete_gem(self, sjw_id, color):
        self.cursor.execute("""
            DELETE FROM sjw_gems
            WHERE sjw_gems_sjw_id = %s AND sjw_gems_color = %s
        """, (sjw_id, color))

