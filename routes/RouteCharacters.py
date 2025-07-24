import json
import os
import psycopg2
from flask import Flask, render_template, url_for, session
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.ControleurConf import ControleurConf

def get_psql_conn():
    conf = ControleurConf()
    host = conf.get_config('PSQL', 'host')
    port = conf.get_config('PSQL', 'port')
    database = conf.get_config('PSQL', 'database')
    user = conf.get_config('PSQL', 'user')
    password = conf.get_config('PSQL', 'password')
    return psycopg2.connect(
        dbname=database,
        user=user,
        password=""
    )

def update_image_paths(description, base_path):
    """
    Met à jour les chemins des images dans une description en ajoutant un cache-busting.
    """
    if not description:
        return description

    # Vérifiez si le chemin commence déjà par le chemin de base
    updated_description = description
    if f"src='{url_for('static', filename=base_path)}/" not in description:
        updated_description = description.replace(
            "src='",
            f"src='{url_for('static', filename=base_path)}/"
        )

    return updated_description.replace("\n", "<br>")

def characters(app: Flask):
    @app.route('/characters')
    def inner_characters():
        # Récupérer la langue sélectionnée
        language = session.get('language', "EN-en")  # Valeur par défaut si aucune langue n'est sélectionnée
        if not language:
            return "Language not set", 400

        # --- JSON désactivé ---
        # with open('data/character.json', 'r', encoding='utf-8') as f:
        #     characters_data = json.load(f)
        # characters_data = next((item.get(language) for item in characters_data if language in item), [])
        # if not characters_data:
        #     return f"No data found for language: {language}", 404
        # with open('data/panoplies.json', 'r', encoding='utf-8') as f:
        #     panoplies_data = json.load(f)
        # panoplies_data = panoplies_data.get(language, {}).get('panoplies', [])
        # if not panoplies_data:
        #     return f"No panoplies data found for language: {language}", 404

        # --- Utilisation BDD ---
        conn = get_psql_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder, ct.character_translations_name
            FROM characters c
            JOIN character_translations ct ON ct.character_translations_characters_id = c.characters_id
            WHERE ct.character_translations_language = %s
        """, (language,))
        characters_data = cursor.fetchall()

        images = []
        character_types = set()
        rarities = set()

        for row in characters_data:
            char_id, char_type, char_rarity, char_alias, char_folder, char_name = row
            type_folder = f"SLA_Personnages_{char_type}"
            base_path = f'static/images/Personnages/{type_folder}/{char_folder}'
            codex_png = f'{base_path}/{char_type}_{char_alias}_Codex.png'
            codex_webp = f'{base_path}/{char_type}_{char_alias}_Codex.webp'
            if os.path.exists(codex_webp):
                image_path = codex_webp.replace('static/', '')
            else:
                image_path = codex_png.replace('static/', '')
            images.append({
                'path': image_path,
                'name': char_name,
                'alias': char_alias,
                'type': char_type,
                'rarity': char_rarity
            })
            character_types.add(char_type)
            rarities.add(char_rarity)

        character_types = sorted(character_types)
        rarities = sorted(rarities)

        cursor.execute("""
            SELECT p.panoplies_name, pt.panoplie_translations_name, pt.panoplie_translations_language
            FROM panoplies p
            JOIN panoplie_translations pt ON pt.panoplie_translations_panoplies_id = p.panoplies_id
            WHERE pt.panoplie_translations_language = %s
        """, (language,))
        panoplies_data = [
            {'name': row[0], 'translation': row[1], 'language': row[2]}
            for row in cursor.fetchall()
        ]

        conn.close()

        return render_template(
            'characters.html',
            images=images,
            character_types=character_types,
            rarities=rarities,
            panoplies=panoplies_data
        )

    @app.route('/characters/<alias>')
    def character_details(alias):
        
        write_log(f"Accès aux détails du personnage: {alias}", log_level="INFO")
        # Récupérer la langue sélectionnée
        language = session.get('language', "EN-en")
        if not language:
            return "Language not set", 400

        # --- JSON désactivé ---
        # with open('data/character.json', 'r', encoding='utf-8') as f:
        #     characters_data = json.load(f)
        # characters_data = next((item.get(language) for item in characters_data if language in item), [])
        # if not characters_data:
        #     return f"No data found for language: {language}", 404
        # with open('data/panoplies.json', 'r', encoding='utf-8') as f:
        #     panoplies_data = json.load(f)
        # panoplies_data = panoplies_data.get(language, {}).get('panoplies', [])
        # if not panoplies_data:
        #     return f"No panoplies data found for language: {language}", 404

        conn = get_psql_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.characters_id, c.characters_type, c.characters_rarity, c.characters_alias, c.characters_folder, ct.character_translations_name, ct.character_translations_description
            FROM characters c
            JOIN character_translations ct ON ct.character_translations_characters_id = c.characters_id
            WHERE ct.character_translations_language = %s AND c.characters_alias = %s
        """, (language, alias))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return "Character not found", 404

        char_id, char_type, char_rarity, char_alias, char_folder, char_name, char_description = row
        type_folder = f"SLA_Personnages_{char_type}"
        personnage_png = f'static/images/Personnages/{type_folder}/{char_folder}/{char_type}_{char_alias}_Personnage.png'
        personnage_webp = f'static/images/Personnages/{type_folder}/{char_folder}/{char_type}_{char_alias}_Personnage.webp'
        if os.path.exists(personnage_webp):
            image_path = personnage_webp.replace('static/', '')
        else:
            image_path = personnage_png.replace('static/', '')

        character_info = {
            'name': char_name,
            'alias': char_alias,
            'type': char_type,
            'rarity': char_rarity,
            'image': image_path,
            'description': char_description,
            'background_image': f'images/Personnages/{type_folder}/BG_{char_type}.webp'
        }

        # Passifs
        cursor.execute("""
            SELECT p.passives_principal, pt.passive_translations_name, pt.passive_translations_description, p.passives_image
            FROM passives p
            JOIN passive_translations pt ON pt.passive_translations_passives_id = p.passives_id
            WHERE p.passives_characters_id = %s AND pt.passive_translations_language = %s
        """, (char_id, language))
        character_info['passives'] = [
            {
                'principal': row[0],
                'name': row[1],
                'description': update_image_paths(row[2], f'images/Personnages/{type_folder}/{char_folder}'),
                'image': f'images/Personnages/{type_folder}/{char_folder}/{row[3]}' if row[3] else ''
            }
            for row in cursor.fetchall()
        ]
        
        # Evolutions du personnage
        cursor.execute("""
            SELECT ce.character_evolutions_evolution_id, ce.character_evolutions_number, ce.character_evolutions_type, ce.character_evolutions_range, cet.character_evolution_translations_description
            FROM character_evolutions ce
            LEFT JOIN character_evolution_translations cet ON cet.character_evolution_translations_character_evolutions_id = ce.character_evolutions_id
            WHERE ce.character_evolutions_characters_id = %s AND (cet.character_evolution_translations_language = %s OR cet.character_evolution_translations_language IS NULL)
        """, (char_id, language))
        character_info['evolutions'] = [
            {
                'id': row[0],
                'number': row[1],
                'type': row[2],
                'range': row[3],
                'description': update_image_paths(row[4], f'images/Personnages/{type_folder}/{char_folder}') if row[4] else ''
            }
            for row in cursor.fetchall()
        ]

        # Skills
        cursor.execute("""
            SELECT s.skills_principal, st.skill_translations_name, st.skill_translations_description, s.skills_image
            FROM skills s
            JOIN skill_translations st ON st.skill_translations_skills_id = s.skills_id
            WHERE s.skills_characters_id = %s AND st.skill_translations_language = %s
        """, (char_id, language))
        character_info['skills'] = [
            {
                'principal': row[0],
                'name': row[1],
                'description': update_image_paths(row[2], f'images/Personnages/{type_folder}/{char_folder}'),
                'image': f'images/Personnages/{type_folder}/{char_folder}/{row[3]}' if row[3] else ''
            }
            for row in cursor.fetchall()
        ]

        # Armes
        cursor.execute("""
            SELECT w.weapons_id, wt.weapon_translations_name, wt.weapon_translations_stats, w.weapons_image
            FROM weapons w
            JOIN weapon_translations wt ON wt.weapon_translations_weapons_id = w.weapons_id
            WHERE w.weapons_characters_id = %s AND wt.weapon_translations_language = %s
        """, (char_id, language))
        weapons = []
        for w_row in cursor.fetchall():
            weapon_id, weapon_name, weapon_stats, weapon_image = w_row
            # Evolutions de l'arme
            cursor.execute("""
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
                    'description': update_image_paths(evo[4], f'images/Personnages/{type_folder}/{char_folder}') if evo[4] else ''
                }
                for evo in cursor.fetchall()
            ]
            weapons.append({
                'name': weapon_name,
                'stats': update_image_paths(weapon_stats, f'images/Personnages/{type_folder}/{char_folder}') if weapon_stats else '',
                'image': f'images/Personnages/{type_folder}/{char_folder}/{weapon_image}' if weapon_image else '',
                'evolutions': evolutions
            })
        character_info['weapon'] = weapons

        # Sets d'équipement
        cursor.execute("""
            SELECT es.equipment_sets_id, es.equipment_sets_name
            FROM equipment_sets es
            WHERE es.equipment_sets_characters_id = %s
        """, (char_id,))
        equipment_sets = []
        for es_row in cursor.fetchall():
            eq_set_id, eq_set_name = es_row
            # Focus stats
            cursor.execute("""
                SELECT equipment_focus_stats_name FROM equipment_focus_stats
                WHERE equipment_focus_stats_equipment_sets_id = %s
            """, (eq_set_id,))
            focus_stats = [fs_row[0] for fs_row in cursor.fetchall()]
            # Artefacts
            cursor.execute("""
                SELECT a.artefacts_id, at.artefact_translations_name, at.artefact_translations_set, a.artefacts_image, a.artefacts_main_stat
                FROM artefacts a
                JOIN artefact_translations at ON at.artefact_translations_artefacts_id = a.artefacts_id
                WHERE a.artefacts_equipment_sets_id = %s AND at.artefact_translations_language = %s
            """, (eq_set_id, language))
            artefacts = []
            for a_row in cursor.fetchall():
                artefact_id, artefact_name, artefact_set, artefact_image, artefact_main_stat = a_row
                # Stats secondaires
                cursor.execute("""
                    SELECT artefact_secondary_stats_name FROM artefact_secondary_stats
                    WHERE artefact_secondary_stats_artefacts_id = %s
                """, (artefact_id,))
                secondary_stats = [sec_row[0] for sec_row in cursor.fetchall()]
                artefacts.append({
                    'name': artefact_name,
                    'set': artefact_set,
                    'image': f'images/Artefacts/{artefact_image}' if artefact_image else '',
                    'main_stat': artefact_main_stat,
                    'secondary_stats': secondary_stats
                })
            # Noyaux
            cursor.execute("""
                SELECT cores_name, cores_number, cores_image, cores_main_stat, cores_secondary_stat
                FROM cores
                WHERE cores_equipment_sets_id = %s
            """, (eq_set_id,))
            cores = [
                {
                    'name': core_row[0],
                    'number': core_row[1],
                    'image': f'images/Noyaux/{core_row[2]}' if core_row[2] else '',
                    'main_stat': core_row[3],
                    'secondary_stat': core_row[4]
                }
                for core_row in cursor.fetchall()
            ]
            equipment_sets.append({
                'set_name': eq_set_name,
                'focus_stats': focus_stats,
                'artefacts': artefacts,
                'cores': cores
            })
        character_info['equipment_sets'] = equipment_sets

        conn.close()

        return render_template('character_details.html', character=character_info, language=language)