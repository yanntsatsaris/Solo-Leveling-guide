import os
import glob
from flask import Flask, render_template, url_for, session, request, redirect, abort, jsonify
from flask_login import login_required, current_user
from routes.utils import *
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
from static.Controleurs.sql_entities.cores_sql import CoresSql

def characters_public_routes(app: Flask):
    @app.route('/characters')
    def inner_characters():
        # Récupérer la langue sélectionnée
        language = session.get('language', "EN-en")  # Valeur par défaut si aucune langue n'est sélectionnée
        if not language:
            return "Language not set", 400

        # --- Utilisation du contrôleur SQL segmenté ---
        sql_manager = ControleurSql()
        characters_sql = CharactersSql(sql_manager.cursor)

        characters_data = characters_sql.get_characters(language)
        panoplies_sql = PanopliesSql(sql_manager.cursor)
        cores_sql = CoresSql(sql_manager.cursor)

        panoplies_effects = panoplies_sql.get_panoplies_effects(language)
        panoplies_names = sorted(list({p['set_name'] for p in panoplies_effects}))
        cores_effects = cores_sql.get_cores_effects(language)
        cores_names = sorted(list({c['color'] for c in cores_effects}))
        sql_manager.close()

        images = []
        character_types = set()
        rarities = set()

        for row in characters_data:
            char_id, char_type, char_rarity, char_alias, char_folder, char_name = row
            type_folder = f"SLA_Personnages_{char_type}"
            if char_folder is None or char_folder.strip() == "":
                char_folder = f"{char_rarity}_{char_type}_{char_alias}"
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
        rarities = sorted(rarities, reverse=True)

        return render_template(
            'characters.html',
            images=images,
            character_types=character_types,
            rarities=rarities,
            panoplies_list=panoplies_names,
            cores_list=cores_names  # Passage à la vue
        )

    @app.route('/characters/<alias>')
    def character_details(alias):
        write_log(f"Accès aux détails du personnage: {alias}", log_level="INFO")
        language = session.get('language', "EN-en")
        if not language:
            return "Language not set", 400

        sql_manager = ControleurSql()
        characters_sql = CharactersSql(sql_manager.cursor)
        passives_sql = PassivesSql(sql_manager.cursor)
        evolutions_sql = EvolutionsSql(sql_manager.cursor)
        skills_sql = SkillsSql(sql_manager.cursor)
        weapons_sql = WeaponsSql(sql_manager.cursor)
        equipment_set_sql = EquipmentSetSql(sql_manager.cursor)
        panoplies_sql = PanopliesSql(sql_manager.cursor)
        cores_sql = CoresSql(sql_manager.cursor)  # Ajout du contrôleur cores

        row = characters_sql.get_character_details(language, alias)
        if not row:
            sql_manager.close()
            return "Character not found", 404

        char_id = row['characters_id']
        char_type = row['characters_type']
        char_rarity = row['characters_rarity']
        char_alias = row['characters_alias']
        char_folder = row['characters_folder']
        char_name = row['character_translations_name']
        char_description = row['character_translations_description']

        type_folder = f"SLA_Personnages_{char_type}"
        if char_folder is None or char_folder.strip() == "":
            char_folder = f"{char_rarity}_{char_type}_{char_alias}"
        personnage_png = f'static/images/Personnages/{type_folder}/{char_folder}/{char_type}_{char_alias}_Personnage.png'
        personnage_webp = f'static/images/Personnages/{type_folder}/{char_folder}/{char_type}_{char_alias}_Personnage.webp'
        if os.path.exists(personnage_webp):
            image_path = personnage_webp.replace('static/', '')
        else:
            image_path = personnage_png.replace('static/', '')

        base_path = f'images/Personnages/{type_folder}/{char_folder}'

        character_info = {
            'id': char_id,
            'name': char_name,
            'alias': char_alias,
            'type': char_type,
            'rarity': char_rarity,
            'image': image_path,
            'image_name': f'{char_type}_{char_alias}_Personnage.webp' if os.path.exists(personnage_webp) else f'{char_type}_{char_alias}_Personnage.png',
            'description': char_description,
            'images_folder' : char_folder
        }

        passives = passives_sql.get_passives(char_id, language, type_folder, char_folder)
        all_passives = passives_sql.get_passives(char_id, language, type_folder, char_folder)

        skills = skills_sql.get_skills(char_id, language, type_folder, char_folder)
        weapons = weapons_sql.get_weapons(char_id, language, type_folder, char_folder)

        # Ajoute le tag de l'arme dans la liste des tags
        all_tags = passives + skills + weapons
        # Filtre les passifs cachés
        passives = [p for p in passives if not p.get('hidden', False)]

        for passive in passives:
            passive['description_raw'] = passive['description']  # version brute
            passive['description'] = process_description(passive['description'], all_tags, base_path)
        character_info['passives'] = passives

        for passive in all_passives:
            passive['description_raw'] = passive['description']  # version brute
            passive['description'] = process_description(passive['description'], all_tags, base_path)
        character_info['passives_all'] = all_passives

        evolutions = evolutions_sql.get_evolutions(char_id, language, type_folder, char_folder)
        for evo in evolutions:
            evo['description_raw'] = evo['description']  # version brute
            evo['description'] = process_description(evo['description'], all_tags, base_path)
        character_info['evolutions'] = evolutions

        for skill in skills:
            skill['description_raw'] = skill['description']  # version brute
            skill['description'] = process_description(skill['description'], all_tags, base_path)
        character_info['skills'] = skills

        # Weapons
        weapons = weapons_sql.get_weapons(char_id, language, type_folder, char_folder)
        for weapon in weapons:
            weapon['stats_raw'] = weapon.get('stats', '')  # version brute
            weapon['stats'] = process_description(weapon.get('stats', ''), all_tags, base_path)
            for evo in weapon.get('evolutions', []):
                evo['description_raw'] = evo['description']  # version brute
                evo['description'] = process_description(evo['description'], all_tags, base_path)
        character_info['weapon'] = weapons

        equipment_sets = []
        for eq_set_id, eq_set_name in equipment_set_sql.get_equipment_sets(char_id, language):
            equipment_sets.append(
                equipment_set_sql.get_equipment_set_details(eq_set_id, eq_set_name, language)
            )
        character_info['equipment_sets'] = equipment_sets
        for eq_set in character_info['equipment_sets']:
            eq_set['description_raw'] = eq_set['description']  # version brute
            eq_set['description'] = process_description(eq_set['description'], all_tags, base_path)

        # Ajout de l'extraction de la couleur des cœurs
        for eq_set in character_info['equipment_sets']:
            for core in eq_set['cores']:
                core['color'] = core['name']

        panoplies_effects = panoplies_sql.get_panoplies_effects(language)
        panoplies_names = sorted(list({p['set_name'] for p in panoplies_effects}))
        cores_effects = cores_sql.get_cores_effects(language)
        cores_names = sorted(list({c['color'] for c in cores_effects}))
        if cores_effects is None:
            cores_effects = []
        sql_manager.close()

        return render_template(
            'character_details.html',
            character=character_info,
            language=language,
            panoplies_effects=panoplies_effects,
            cores_effects=cores_effects,  # Passage à la vue
            panoplies_list=panoplies_names,
            cores_list=cores_names  # Passage à la vue
        )
