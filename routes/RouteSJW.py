import json
import os
import re
import unicodedata
import glob
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.ControleurSql import ControleurSql
from static.Controleurs.sql_entities.sjw_sql import SJWSql
from static.Controleurs.sql_entities.sjw.sjw_skills_sql import SJWSkillsSql
from static.Controleurs.sql_entities.sjw.sjw_shadows_sql import SJWShadowsSql
from static.Controleurs.sql_entities.sjw.sjw_weapons_sql import SJWWeaponsSql
from static.Controleurs.sql_entities.sjw.sjw_equipment_set_sql import SJWEquipmentSetSql
from static.Controleurs.sql_entities.sjw.sjw_blessings_sql import SJWBlessingsSql
from static.Controleurs.sql_entities.cores_sql import CoresSql
from static.Controleurs.sql_entities.panoplies_sql import PanopliesSql
from flask import Flask, render_template, session , url_for
from flask_login import login_required

def normalize_focus_stats(val):
    if isinstance(val, list):
        # Si la liste contient une seule chaîne avec des virgules, découpe-la
        if len(val) == 1 and isinstance(val[0], str) and ',' in val[0]:
            return sorted([v.strip() for v in val[0].split(',') if v.strip()])
        return sorted([v.strip() for v in val if v])
    if isinstance(val, str):
        return sorted([v.strip() for v in val.split(',') if v.strip()])
    return []

def normalize_stats(val):
    if isinstance(val, list):
        return ','.join([v.strip() for v in val if v])
    if isinstance(val, str):
        return ','.join([v.strip() for v in val.split(',') if v.strip()])
    return ''

def normalize_text(val):
    if val is None:
        return ''
    # Unifie les retours à la ligne et supprime les espaces superflus
    return val.replace('\r\n', '\n').replace('\r', '\n').strip()

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

def none_to_empty(val):
    return "None" if val == "" else val

def SJW(app: Flask):
    @app.route('/SJW')
    def inner_SJW():
        write_log("Accès à la page SJW", log_level="INFO")
        language = session.get('language', "EN-en")
        sql_manager = ControleurSql()
        sjw_sql = SJWSql(sql_manager.cursor)
        shadows_sql = SJWShadowsSql(sql_manager.cursor)
        skills_sql = SJWSkillsSql(sql_manager.cursor)
        weapons_sql = SJWWeaponsSql(sql_manager.cursor)
        equipment_set_sql = SJWEquipmentSetSql(sql_manager.cursor)
        blessings_sql = SJWBlessingsSql(sql_manager.cursor)
        panoplies_sql = PanopliesSql(sql_manager.cursor)
        cores_sql = CoresSql(sql_manager.cursor)

        # Récupération des infos principales
        character_info = sjw_sql.get_sjw(language)
        folder = character_info['folder']
        base_path = f'images/{folder}'
        character_info['image'] = f'images/{folder}/Sung_Jinwoo.png'
        
        all_tags = []
        
        # Récupération des shadows (avec évolutions)
        character_info['shadows'] = shadows_sql.get_shadows(character_info['id'], language, folder)

        # Récupération des skills
        character_info['skills'] = skills_sql.get_skills(character_info['id'], language)

        # Récupération des armes (avec évolutions)
        character_info['weapon'] = weapons_sql.get_weapons(character_info['id'], language, folder)

        # Récupération des sets d'équipement (avec artefacts et cores)
        equipment_sets = []
        for eq_set_id, eq_set_name in equipment_set_sql.get_equipment_sets(character_info['id'], language):
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

        # Récupération des bénédictions
        character_info['offensive_blessings'] = blessings_sql.get_offensive_blessings(character_info['id'])
        character_info['defensive_blessings'] = blessings_sql.get_defensive_blessings(character_info['id'])

        # Récupération des panoplies et noyaux (si besoin pour le contexte global)
        panoplies_effects = panoplies_sql.get_panoplies_effects(language)
        cores_effects = cores_sql.get_cores_effects(language)

        sql_manager.close()

        return render_template(
            'SJW.html',
            character=character_info,
            language=language,
            panoplies_effects=panoplies_effects,
            cores_effects=cores_effects,  # Passage à la vue
        )

    @app.route('/SJW/shadow/<shadowName>')
    def shadow_details(shadowName):
        # Récupérer la langue sélectionnée
        language = session.get('language', "EN-en")
        if not language:
            return "Language not set", 400

        # Charger les données des personnages depuis le fichier JSON
        with open('data/SJW.json', 'r', encoding='utf-8') as f:
            characters_data = json.load(f)

        # Trouver les données correspondant à la langue sélectionnée
        characters_data = next((item.get(language) for item in characters_data if language in item), [])
        if not characters_data:
            return f"No data found for language: {language}", 404

        # Trouver l'ombre correspondant au nom donné
        shadow = None
        character_folder = None
        for character in characters_data:
            for s in character.get('shadows', []):
                if s['name'] == shadowName:
                    shadow = s
                    character_folder = character['folder']
                    # Mettre à jour les chemins des images
                    if 'image' in shadow:
                        shadow['image'] = f'images/{character_folder}/Shadows/{shadow["image"]}'
                    if 'description' in shadow:
                        shadow['description'] = update_image_paths(shadow['description'], f'images/{character_folder}')
                    
                    # Mettre à jour les compétences (skills) de l'ombre
                    for skill in shadow.get('skills', []):
                        if 'image' in skill:
                            skill['image'] = f'images/{character_folder}/Shadows/Skills/{skill["image"]}'
                        if 'description' in skill:
                            skill['description'] = update_image_paths(skill['description'], f'images/{character_folder}/Shadows/Skills')

                    # Mettre à jour les évolutions de l'ombre
                    for evolution in shadow.get('evolutions', []):
                        if 'description' in evolution:
                            evolution['description'] = update_image_paths(evolution['description'], f'images/{character_folder}/Shadows/Evolutions')

                    # Mettre à jour l'arme associée à l'ombre
                    if 'weapon' in shadow:
                        for weapon in shadow['weapon']:  # <-- Correction ici
                            if 'image' in weapon:
                                weapon['image'] = f'images/{character_folder}/Shadows/Weapons/{weapon["image"]}'
                            if 'codex' in weapon:
                                weapon['codex'] = f'images/{character_folder}/Shadows/Weapons/{weapon["codex"]}'
                            if 'stats' in weapon:
                                weapon['stats'] = update_image_paths(weapon['stats'], f'images/{character_folder}/Shadows/Weapons')
                            for evolution in weapon.get('evolutions', []):
                                if 'description' in evolution:
                                    evolution['description'] = update_image_paths(evolution['description'], f'images/{character_folder}/Shadows/Weapons/Evolutions')

                    break

        if not shadow:
            return "Shadow not found", 404

        # Renvoyer le template avec les données de l'ombre
        return render_template('shadow_details.html', shadow=shadow)

    @app.route('/SJW/weapon/<weaponName>')
    def weapon_details(weaponName):
        # Récupérer la langue sélectionnée
        language = session.get('language', "EN-en")
        if not language:
            return "Language not set", 400

        # Charger les données des personnages depuis le fichier JSON
        with open('data/SJW.json', 'r', encoding='utf-8') as f:
            characters_data = json.load(f)

        # Trouver les données correspondant à la langue sélectionnée
        characters_data = next((item.get(language) for item in characters_data if language in item), [])
        if not characters_data:
            return f"No data found for language: {language}", 404

        # Trouver l'arme correspondant au nom donné
        weapon = None
        character_folder = None
        for character in characters_data:
            for w in character.get('weapon', []):
                if w['name'] == weaponName:
                    weapon = w
                    character_folder = character['folder']
                    # Mettre à jour les chemins des images
                    if 'image' in weapon:
                        weapon['image'] = f'images/{character_folder}/Armes/{weapon["folder"]}/{weapon["image"]}'
                    if 'codex' in weapon:
                        weapon['codex'] = f'images/{character_folder}/Armes/{weapon["folder"]}/{weapon["codex"]}'
                    if 'stats' in weapon:
                        weapon['stats'] = update_image_paths(weapon['stats'], f'images/{character_folder}')
                    for evolution in weapon.get('evolutions', []):
                        if 'description' in evolution:
                            evolution['description'] = update_image_paths(evolution['description'], f'images/{character_folder}')
                    break

        if not weapon:
            return "Weapon not found", 404

        # Renvoyer le template avec les données de l'arme
        return render_template('weapon_details.html', weapon=weapon)
    
    @app.route('/SJW/edit', methods=['GET'])
    @login_required
    def edit_sjw():
        # Vérifier les droits de l'utilisateur
        if not session.get('rights') or not any(right in session['rights'] for right in ['Admin', 'SuperAdmin']):
            return "Access denied", 403

        language = session.get('language', "EN-en")
        sql_manager = ControleurSql()
        sjw_sql = SJWSql(sql_manager.cursor)
        shadows_sql = SJWShadowsSql(sql_manager.cursor)
        skills_sql = SJWSkillsSql(sql_manager.cursor)
        weapons_sql = SJWWeaponsSql(sql_manager.cursor)
        equipment_set_sql = SJWEquipmentSetSql(sql_manager.cursor)
        blessings_sql = SJWBlessingsSql(sql_manager.cursor)

        # Récupération des infos principales
        character_info = sjw_sql.get_sjw(language)
        folder = character_info['folder']