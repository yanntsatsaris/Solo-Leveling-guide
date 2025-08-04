import json
import os
import re
import unicodedata
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

def render_tags(description, tags_list, base_path):

    def normalize_tag(tag):
        # Remplace tous les types d'apostrophes par une apostrophe simple
        tag = tag.replace("’", "'").replace("`", "'").replace("´", "'")
        # Supprime les accents et met en minuscule
        return ''.join(
            c for c in unicodedata.normalize('NFD', tag)
            if unicodedata.category(c) != 'Mn'
        ).lower().strip()

    def find_tag(tag):
        tag_norm = normalize_tag(tag)
        for item in tags_list:
            tag_value = item.get('tag')
            if tag_value and normalize_tag(tag_value) == tag_norm:
                return item
        return None

    def replacer(match):
        tag_raw = match.group(1)
        parts = tag_raw.split('|')
        tag = parts[0].strip()
        only_img = len(parts) > 1 and parts[1].strip().lower() == 'img'
        tag_info = find_tag(tag)
        if tag_info and tag_info.get('image'):
            img_path = tag_info['image']
            if not img_path.startswith('images/'):
                img_url = url_for('static', filename=f"{base_path}/{img_path}")
            else:
                img_url = url_for('static', filename=img_path)
            img_html = f"<img src='{img_url}' alt='{tag_info.get('tag', tag)}' class='tag-img'>"
            if only_img:
                return img_html
            else:
                return f"{img_html} [{tag_info.get('tag', tag)}]"
        return match.group(0)

    result = re.sub(r"\[([^\]]+)\]", replacer, description).replace("\n", "<br>")
    return result

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

def process_description(description, tags_list, base_path):
    if not description:
        return description
    if re.search(r"<img\s+src=.*?>\s*\[[^\]]+\]", description):
        return update_image_paths(description, base_path)
    elif re.search(r"\[[^\]]+\]", description):
        return render_tags(description, tags_list, base_path)
    else:
        return description.replace("\n", "<br>")

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

        base_path = f'images/Personnages/{type_folder}/{char_folder}'

        character_info = {
            'name': char_name,
            'alias': char_alias,
            'type': char_type,
            'rarity': char_rarity,
            'image': image_path,
            'description': char_description,
            'background_image': f'images/Personnages/{type_folder}/BG_{char_type}.webp'
        }

        passives = passives_sql.get_passives(char_id, language, type_folder, char_folder)
        # Filtre les passifs cachés
        passives = [p for p in passives if not p.get('hidden', False)]

        skills = skills_sql.get_skills(char_id, language, type_folder, char_folder)
        weapons = weapons_sql.get_weapons(char_id, language, type_folder, char_folder)

        # Ajoute le tag de l'arme dans la liste des tags
        all_tags = passives + skills + weapons

        for passive in passives:
            passive['description'] = process_description(passive['description'], all_tags, base_path)
        character_info['passives'] = passives

        evolutions = evolutions_sql.get_evolutions(char_id, language, type_folder, char_folder)
        for evo in evolutions:
            evo['description'] = process_description(evo['description'], all_tags, base_path)
        character_info['evolutions'] = evolutions

        for skill in skills:
            skill['description'] = process_description(skill['description'], all_tags, base_path)
        character_info['skills'] = skills

        for weapon in weapons:
            weapon['stats'] = process_description(weapon.get('stats', ''), all_tags, base_path)
            for evo in weapon.get('evolutions', []):
                evo['description'] = process_description(evo['description'], all_tags, base_path)
        character_info['weapon'] = weapons

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

        # ici laisse les commentaire pour le JSON