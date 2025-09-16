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
from flask import Flask, render_template, session , request, redirect, url_for, jsonify
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
        
        skills = skills_sql.get_skills(character_info['id'], language)
        blessings_defensive = blessings_sql.get_defensive_blessings(character_info['id'], language)
        blessings_offensive = blessings_sql.get_offensive_blessings(character_info['id'], language)
        weapons = weapons_sql.get_weapons(character_info['id'], language)
        shadows = shadows_sql.get_shadows(character_info['id'], language, folder)
        
        # Ajoute le tag de l'arme dans la liste des tags
        all_tags = blessings_defensive + blessings_offensive + skills + weapons + shadows
        
        # Récupération des shadows (avec évolutions)
        for shadow in shadows:
            shadow['description_raw'] = shadow['description']  # version brute
            shadow['description'] = process_description(shadow['description'], all_tags, base_path)
            for skill in shadow.get('skills', []):
                skill['description_raw'] = skill['description']  # version brute
                skill['description'] = process_description(skill['description'], all_tags, base_path)
            for evolution in shadow.get('evolutions', []):
                evolution['description_raw'] = evolution['description']  # version brute
                evolution['description'] = process_description(evolution['description'], all_tags, base_path)
            for weapon in shadow.get('weapon', []):
                weapon['description_raw'] = weapon['description']  # version brute
                weapon['description'] = process_description(weapon['description'], all_tags, base_path)
                for evolution in weapon.get('evolutions', []):
                    evolution['description_raw'] = evolution['description']  # version brute
                    evolution['description'] = process_description(evolution['description'], all_tags, base_path)
        character_info['shadows'] = shadows

        for blessing in blessings_defensive:
            blessing['description_raw'] = blessing['description']  # version brute
            blessing['description'] = process_description(blessing['description'], all_tags, base_path)
        character_info['defensive_blessings'] = blessings_defensive
        
        for blessing in blessings_offensive:
            blessing['description_raw'] = blessing['description']  # version brute
            blessing['description'] = process_description(blessing['description'], all_tags, base_path)
        character_info['offensive_blessings'] = blessings_offensive
        
        # Récupération des skills
        for skill in skills:
            skill['description_raw'] = skill['description']  # version brute
            skill['description'] = process_description(skill['description'], all_tags, base_path)
            for evolution in skill.get('evolutions', []):
                evolution['description_raw'] = evolution['description']  # version brute
                evolution['description'] = process_description(evolution['description'], all_tags, base_path)
        character_info['skills'] = skills
        
        # Récupération des armes (avec évolutions)
        for weapon in weapons:
            weapon['stats_raw'] = weapon.get('stats', '')  # version brute
            weapon['stats'] = process_description(weapon.get('stats', ''), all_tags, base_path)
            for evolution in weapon.get('evolutions', []):
                evolution['description_raw'] = evolution['description']  # version brute
                evolution['description'] = process_description(evolution['description'], all_tags, base_path)
        character_info['weapon'] = weapons
        write_log(f"Armes récupérées : {weapons}", log_level="INFO")

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

        # Récupération des panoplies et noyaux (si besoin pour le contexte global)
        panoplies_effects = panoplies_sql.get_panoplies_effects(language)
        panoplies_names = sorted(list({p['set_name'] for p in panoplies_effects}))
        cores_effects = cores_sql.get_cores_effects(language)
        cores_names = sorted(list({c['color'] for c in cores_effects}))

        sql_manager.close()

        return render_template(
            'SJW.html',
            character=character_info,
            language=language,
            panoplies_effects=panoplies_effects,
            cores_effects=cores_effects,  # Passage à la vue
            panoplies_list=panoplies_names,
            cores_list=cores_names  # Passage à la vue
        )

    @app.route('/SJW/shadow/<shadowName>')
    def shadow_details(shadowName):
        language = session.get('language', "EN-en")
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        sjw_sql = SJWSql(cursor)
        shadows_sql = SJWShadowsSql(cursor)

        character_info = sjw_sql.get_sjw(language)
        sjw_id = character_info['id']
        folder = character_info['folder']

        # Récupère toutes les infos de la shadow via la BDD
        shadow = shadows_sql.get_shadow_details(sjw_id, shadowName, language, folder)
        sql_manager.close()
        if not shadow:
            return "Shadow not found", 404

        # Formatage des descriptions (optionnel, comme dans inner_SJW)
        base_path = f'images/{folder}'
        all_tags = []  # Ajoute ici la liste des tags si besoin
        shadow['description_raw'] = shadow['description']
        shadow['description'] = process_description(shadow['description'], all_tags, base_path)
        for skill in shadow.get('skills', []):
            skill['description_raw'] = skill['description']
            skill['description'] = process_description(skill['description'], all_tags, base_path)
        for evolution in shadow.get('evolutions', []):
            evolution['description_raw'] = evolution['description']
            evolution['description'] = process_description(evolution['description'], all_tags, base_path)
            for passive in evolution.get('authority_passives', []):
                passive['description_raw'] = passive['description']
                passive['description'] = process_description(passive['description'], all_tags, base_path)
        if shadow.get('weapon'):
            shadow['weapon']['description_raw'] = shadow['weapon'].get('description', '')
            shadow['weapon']['description'] = process_description(shadow['weapon'].get('description', ''), all_tags, base_path)
            for evolution in shadow['weapon'].get('evolutions', []):
                evolution['description_raw'] = evolution['description']
                evolution['description'] = process_description(evolution['description'], all_tags, base_path)

        # Authority passives directes (si présentes)
        for passive in shadow.get('authority_passives', []):
            passive['description_raw'] = passive['description']
            passive['description'] = process_description(passive['description'], all_tags, base_path)

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
    
    @app.route('/SJW/edit', methods=['POST'])
    @login_required
    def edit_sjw():
        # Vérifier les droits de l'utilisateur
        if not session.get('rights') or not any(right in session['rights'] for right in ['Admin', 'SuperAdmin']):
            return "Access denied", 403

        language = session.get('language', "EN-en")
        name = request.form.get('name')
        alias = request.form.get('alias')
        description = request.form.get('description')
        char_folder = request.form.get('folder')
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor

        sjw_sql = SJWSql(cursor)
        current_character = sjw_sql.get_sjw(language)
        
        char_id = current_character['id']

        char_modif = False
        if (
            (current_character['name'] or '') != (name or '') or
            current_character['alias'] != alias or
            (current_character['description'] or '') != (description or '')
        ):
            sjw_sql.update_sjw(
                sjw_id=char_id,
                alias=alias,
                name=name,
                description=description,
                language=language
            )
            char_modif = True
            write_log(f"Modification personnage {char_id} ({alias})", log_level="INFO")

        
        # --- Sets d'équipement, artefacts et noyaux ---
        equipment_set_sql = SJWEquipmentSetSql(cursor)
        current_sets = equipment_set_sql.get_equipment_sets_full(char_id, language)
        existing_set_ids = [str(s['id']) for s in current_sets]
        form_set_ids = []
        set_modif = False
        set_idx = 0
        while True:
            set_name = request.form.get(f"eqset_name_{set_idx}")
            if set_name is None:
                break
            set_desc = request.form.get(f"eqset_description_{set_idx}")
            set_focus = request.form.get(f"eqset_focus_stats_{set_idx}")
            set_order = request.form.get(f"eqset_order_{set_idx}")
            set_id = request.form.get(f"eqset_id_{set_idx}")
            db_set = next((s for s in current_sets if str(s['id']) == str(set_id)), None) if set_id else None
            if set_id:
                if db_set and (
                    (db_set['name'] or '') != (set_name or '') or
                    (db_set['description'] or '') != (set_desc or '') or
                    not focus_stats_equal(db_set['focus_stats'], set_focus) or
                    (str(db_set['order']) or '') != (str(set_order) or '')
                ):
                    equipment_set_sql.update_equipment_set(set_id, char_id, set_name, set_desc, set_focus, set_order, language)
                    set_modif = True
                    write_log(f"Modification set {set_id} du personnage {char_id}", log_level="INFO")
                form_set_ids.append(set_id)
            else:
                set_id = equipment_set_sql.add_equipment_set(char_id, set_name, set_desc, set_focus, set_order, language)
                set_modif = True
                write_log(f"Ajout set {set_id} au personnage {char_id}", log_level="INFO")
                form_set_ids.append(set_id)
            # --- Artefacts du set ---
            current_artefacts = db_set['artefacts'] if set_id and db_set and 'artefacts' in db_set else []
            existing_artefact_ids = [str(a['id']) for a in current_artefacts]
            form_artefact_ids = []
            for artefact_idx in range(8):
                aname = request.form.get(f"artefact_name_{set_idx}_{artefact_idx}")
                aset = request.form.get(f"artefact_set_{set_idx}_{artefact_idx}")
                # aimg = request.form.get(f"artefact_image_{set_idx}_{artefact_idx}")  # <-- Supprime cette ligne
                amain = request.form.get(f"artefact_main_stat_{set_idx}_{artefact_idx}")
                asec = request.form.get(f"artefact_secondary_stats_{set_idx}_{artefact_idx}")
                aid = request.form.get(f"artefact_id_{set_idx}_{artefact_idx}")

                # Recherche automatique de l'image
                aset_folder = (aset or '').replace(' ', '_')
                artefact_folder = os.path.join('static', 'images', 'Artefacts', aset_folder)
                pattern = os.path.join(artefact_folder, f"Artefact0{artefact_idx + 1}_*")
                found_images = glob.glob(pattern)
                if found_images:
                    aimg = os.path.basename(found_images[0])
                else:
                    aimg = ""

                db_artefact = next((a for a in current_artefacts if str(a['id']) == str(aid)), None) if aid else None
                if aid:
                    if db_artefact and (
                        (db_artefact['name'] or '') != (aname or '') or
                        (db_artefact['set'] or '') != (aset or '') or
                        (db_artefact['image_name'] or '') != (aimg or '') or
                        (db_artefact['main_stat'] or '') != (amain or '') or
                        normalize_stats(db_artefact['secondary_stats']) != normalize_stats(asec)
                    ):
                        equipment_set_sql.update_artefact(aid, set_id, aname, aset, aimg, amain, asec, language)
                        set_modif = True
                        write_log(f"Modification artefact {aid} du set {set_id}", log_level="INFO")
                    form_artefact_ids.append(aid)
                else:
                    new_aid = equipment_set_sql.add_artefact(set_id, aname, aset, aimg, amain, asec, language)
                    set_modif = True
                    write_log(f"Ajout artefact {new_aid} au set {set_id}", log_level="INFO")
                    form_artefact_ids.append(new_aid)
            for db_id in existing_artefact_ids:
                if str(db_id) not in form_artefact_ids:
                    equipment_set_sql.delete_artefact(db_id)
                    set_modif = True
                    write_log(f"Suppression artefact {db_id} du set {set_id}", log_level="INFO")
            # --- Noyaux du set ---
            current_cores = db_set['cores'] if set_id and db_set and 'cores' in db_set else []
            existing_core_ids = [str(c['id']) for c in current_cores]
            form_core_ids = []
            for core_idx in range(3):
                cname = request.form.get(f"core_name_{set_idx}_{core_idx}")
                #cimg = request.form.get(f"core_image_{set_idx}_{core_idx}")
                cmain = request.form.get(f"core_main_stat_{set_idx}_{core_idx}")
                csec = request.form.get(f"core_secondary_stat_{set_idx}_{core_idx}")
                cid = request.form.get(f"core_id_{set_idx}_{core_idx}")
                cnumber = f"{core_idx+1:02d}"  # Ajoute cette ligne pour numéroter 01, 02, 03
                cimg = cname + cnumber + ".webp"  # Utilise le nom du noyau et le numéro pour l'image
                db_core = next((c for c in current_cores if str(c['id']) == str(cid)), None) if cid else None
                if cid:
                    if db_core and (
                        db_core['name'] != cname or
                        db_core['main_stat'] != cmain or
                        db_core['secondary_stat'] != csec or
                        str(db_core.get('number', '')) != cnumber
                    ):
                        equipment_set_sql.update_core(cid, set_id, cname, cimg, cmain, csec, cnumber, language)
                        set_modif = True
                        write_log(f"Modification noyau {cid} du set {set_id}", log_level="INFO")
                    form_core_ids.append(cid)
                else:
                    new_cid = equipment_set_sql.add_core(set_id, cname, cimg, cmain, csec, cnumber, language)
                    set_modif = True
                    write_log(f"Ajout noyau {new_cid} au set {set_id}", log_level="INFO")
                    form_core_ids.append(new_cid)
            # <-- Boucle de suppression déplacée ici
            for db_id in existing_core_ids:
                if str(db_id) not in form_core_ids:
                    equipment_set_sql.delete_core(db_id)
                    set_modif = True
                    write_log(f"Suppression noyau {db_id} du set {set_id}", log_level="INFO")
            set_idx += 1
        for db_id in existing_set_ids:
            if str(db_id) not in form_set_ids:
                equipment_set_sql.delete_equipment_set(db_id)
                set_modif = True
                write_log(f"Suppression set {db_id} du personnage {char_id}", log_level="INFO")

        sql_manager.conn.commit()
        sql_manager.close()

        # Log global
        if not (char_modif or set_modif):
            write_log(f"Aucune modification détectée pour le personnage {char_id}", log_level="INFO")

        return redirect(url_for('inner_SJW'))
        
    @app.route('/SJW/images_for/<folder>')
    @login_required
    def images_for_SJW(folder):
        # Sécurise les noms
        folder = folder.replace('..', '').replace('/', '').replace('\\', '')
        img_dir = os.path.join('static', 'images', folder)
        if not os.path.isdir(img_dir):
            write_log(f"Le dossier d'images n'existe pas : {img_dir}", log_level="WARNING")
            return jsonify([])
        images = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))])
        return jsonify(images)
    
def focus_stats_equal(a, b):
    return set(normalize_focus_stats(a)) == set(normalize_focus_stats(b))