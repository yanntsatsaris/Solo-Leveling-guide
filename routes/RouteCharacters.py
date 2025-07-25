import json
import os
from flask import Flask, render_template, url_for, session
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.ControleurConf import ControleurConf
from static.Controleurs.ControleurSql import ControleurSql

# Import des entités SQL segmentées
from static.Controleurs.sql_entities.characters_sql import CharactersSql
from static.Controleurs.sql_entities.panoplies_sql import PanopliesSql
from static.Controleurs.sql_entities.characters.passives_sql import PassivesSql
from static.Controleurs.sql_entities.characters.evolutions_sql import EvolutionsSql
from static.Controleurs.sql_entities.characters.skills_sql import SkillsSql
from static.Controleurs.sql_entities.characters.weapons_sql import WeaponsSql
from static.Controleurs.sql_entities.characters.equipment_set_sql import EquipmentSetSql

def update_image_paths(description, base_path):
    """
    Met à jour les chemins des images dans une description en ajoutant un cache-busting.
    """
    if not description:
        return description
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

        # --- Utilisation du contrôleur SQL segmenté ---
        sql_manager = ControleurSql()
        characters_sql = CharactersSql(sql_manager.cursor)
        panoplies_sql = PanopliesSql(sql_manager.cursor)

        characters_data = characters_sql.get_characters(language)
        panoplies_data = panoplies_sql.get_panoplies(language)
        sql_manager.close()

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

        panoplies_data = [
            {'name': row[0], 'translation': row[1], 'language': row[2]}
            for row in panoplies_data
        ]

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

        sql_manager = ControleurSql()
        characters_sql = CharactersSql(sql_manager.cursor)
        passives_sql = PassivesSql(sql_manager.cursor)
        evolutions_sql = EvolutionsSql(sql_manager.cursor)
        skills_sql = SkillsSql(sql_manager.cursor)
        weapons_sql = WeaponsSql(sql_manager.cursor)
        equipment_set_sql = EquipmentSetSql(sql_manager.cursor)
        panoplies_sql = PanopliesSql(sql_manager.cursor)

        row = characters_sql.get_character_details(language, alias)
        if not row:
            sql_manager.close()
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

        character_info['passives'] = passives_sql.get_passives(char_id, language, type_folder, char_folder, update_image_paths)
        character_info['evolutions'] = evolutions_sql.get_evolutions(char_id, language, type_folder, char_folder, update_image_paths)
        character_info['skills'] = skills_sql.get_skills(char_id, language, type_folder, char_folder, update_image_paths)
        character_info['weapon'] = weapons_sql.get_weapons(char_id, language, type_folder, char_folder, update_image_paths)

        equipment_sets = []
        for eq_set_id, eq_set_name in equipment_set_sql.get_equipment_sets(char_id, language):
            equipment_sets.append(
                equipment_set_sql.get_equipment_set_details(eq_set_id, eq_set_name, language)
            )
        character_info['equipment_sets'] = equipment_sets

        panoplies_effects = panoplies_sql.get_panoplies_effects(language)
        sql_manager.close()

        return render_template(
            'character_details.html',
            character=character_info,
            language=language,
            panoplies_effects=panoplies_effects
        )