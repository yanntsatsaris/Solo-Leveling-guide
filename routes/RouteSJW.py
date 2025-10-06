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
from static.Controleurs.sql_entities.sjw.sjw_gems_sql import SJWGemsSql
from static.Controleurs.sql_entities.cores_sql import CoresSql
from static.Controleurs.sql_entities.panoplies_sql import PanopliesSql
from flask import Flask, render_template, session , request, redirect, url_for, jsonify, abort
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
        gems_sql = SJWGemsSql(sql_manager.cursor)
        panoplies_sql = PanopliesSql(sql_manager.cursor)
        cores_sql = CoresSql(sql_manager.cursor)
        

        # Récupération des infos principales
        character_info = sjw_sql.get_sjw(language)
        folder = character_info['folder']
        base_path = f'images/{folder}'
        character_info['image'] = f'images/{folder}/SJW_Personnage.webp'
        
        weapon_types = set()
        rarities = set()
        
        skills = skills_sql.get_skills(character_info['id'], language)
        blessings_defensive = blessings_sql.get_defensive_blessings(character_info['id'], language)
        blessings_offensive = blessings_sql.get_offensive_blessings(character_info['id'], language)
        weapons = weapons_sql.get_weapons(character_info['id'], language, folder)
        shadows = shadows_sql.get_shadows(character_info['id'], language, folder)
        gems = gems_sql.get_gems(character_info['id'])
        
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
            weapon_types.add(weapon['type'])
            rarities.add(weapon['rarity'])
        character_info['weapon'] = weapons

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
                
        character_info['gems'] = gems

        # Récupération des panoplies et noyaux (si besoin pour le contexte global)
        panoplies_effects = panoplies_sql.get_panoplies_effects(language)
        panoplies_names = sorted(list({p['set_name'] for p in panoplies_effects}))
        cores_effects = cores_sql.get_cores_effects(language)
        cores_names = sorted(list({c['color'] for c in cores_effects}))

        sql_manager.close()
        weapon_types = sorted(list(weapon_types))
        rarities = sorted(list(rarities), reverse=True)

        return render_template(
            'SJW.html',
            character=character_info,
            language=language,
            panoplies_effects=panoplies_effects,
            cores_effects=cores_effects,  # Passage à la vue
            panoplies_list=panoplies_names,
            cores_list=cores_names,  # Passage à la vue
            weapon_types=weapon_types,
            rarities=rarities
        )

    @app.route('/SJW/shadow/<shadowAlias>')
    def shadow_details(shadowAlias):
        language = session.get('language', "EN-en")
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        sjw_sql = SJWSql(cursor)
        shadows_sql = SJWShadowsSql(cursor)

        character_info = sjw_sql.get_sjw(language)
        sjw_id = character_info['id']
        folder = character_info['folder']

        # Récupère toutes les infos de la shadow via la BDD
        shadow = shadows_sql.get_shadow_details(sjw_id, shadowAlias, language, folder)
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
    
    @app.route('/SJW/add_shadow/check_image_folder_shadow')
    @login_required
    def check_image_folder_shadow():
        alias = request.args.get('alias', '').replace(' ', '_')
        folder_name = f"Shadow_{alias}"
        folder_path = os.path.join(
            'static', 'images', 'Sung_Jinwoo', 'Shadows', folder_name
        )
        write_log(f"Vérification de l'existence du dossier : {folder_path}", log_level="INFO")
        exists = os.path.isdir(folder_path)
        return jsonify({'exists': exists, 'folder': folder_name})
    
    @app.route('/SJW/add_shadow', methods=['POST'])
    @login_required
    def add_shadow():
        write_log("Tentative d'ajout d'une nouvelle ombre", log_level="INFO")
        # Vérification des droits
        if not session.get('username') or not session.get('rights') or not ('Admin' in session['rights'] or 'SuperAdmin' in session['rights']):
            abort(403)

        language = session.get('language', "EN-en")
        name = request.form.get('name')
        alias = request.form.get('alias')
        description = request.form.get('description')
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        sjw_sql = SJWSql(cursor)
        character_info = sjw_sql.get_sjw(language)
        sjw_id = character_info['id']

        shadow_sql = SJWShadowsSql(cursor)
        new_shadow_id = shadow_sql.add_shadow(sjw_id, alias, name, description, language)
        write_log(f"Nouvelle ombre ajoutée avec l'ID {new_shadow_id} ({alias})", log_level="INFO")
        
        for evo_idx in range(5):
            evolution_id = request.form.get(f"shadows_evolutions_{evo_idx}_evolution_id")
            if not evolution_id or len(evolution_id) > 10:
                evolution_id = f"A{evo_idx}"
            edesc = request.form.get(f'evolution_description_{evo_idx}')
            evo_type = "passive"
            evo_range = None
            evo_number =  evo_idx
            if evolution_id and edesc:
                shadow_sql.add_evolution(new_shadow_id, evo_number, evolution_id, edesc, evo_type, evo_range, language)
                write_log(f"  - Évolution ajoutée : {evolution_id}", log_level="INFO")

        if not new_shadow_id:
            return "Error adding shadow", 500
        
        sql_manager.conn.commit()
        sql_manager.close()
        
        write_log(f"Ombre {new_shadow_id} ({alias}) ajoutée avec succès", log_level="INFO")
        return redirect(url_for('shadow_details', shadowAlias=alias))

    @app.route('/SJW/weapon/<weaponAlias>')
    def weapon_details(weaponAlias):
        language = session.get('language', "EN-en")
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        sjw_sql = SJWSql(cursor)
        weapon_sql = SJWWeaponsSql(cursor)

        character_info = sjw_sql.get_sjw(language)
        sjw_id = character_info['id']
        folder = character_info['folder']

        # Récupère toutes les infos de l'arme via la BDD
        weapon = weapon_sql.get_weapon_details(weaponAlias, language, folder)
        sql_manager.close()
        if not weapon:
            return "Weapon not found", 404

        # Trouver l'arme correspondant au nom donné
        base_path = f'images/{folder}'
        all_tags = []  # Ajoute ici la liste des tags si besoin
        character_folder = None
        if 'evolutions' in weapon and isinstance(weapon['evolutions'], list):
            for evolution in weapon['evolutions']:
                evolution['description_raw'] = evolution['description']
                evolution['description'] = process_description(evolution['description'], all_tags, base_path)

        # Renvoyer le template avec les données de l'arme
        return render_template('weapon_details.html', weapon=weapon)
    
    @app.route('/SJW/add_weapon/check_image_folder_weapon')
    @login_required
    def check_image_folder_weapon():
        alias = request.args.get('alias', '').replace(' ', '_')
        type = request.args.get('type')
        folder_name = f"{type}_{alias}"
        folder_path = os.path.join(
            'static', 'images', 'Sung_Jinwoo', 'Armes', folder_name
        )
        write_log(f"Vérification de l'existence du dossier : {folder_path}", log_level="INFO")
        exists = os.path.isdir(folder_path)
        return jsonify({'exists': exists, 'folder': folder_name})
    
    @app.route('/SJW/add_weapon', methods=['POST'])
    @login_required
    def add_weapon():
        write_log("Tentative d'ajout d'une nouvelle arme", log_level="INFO")
        # Vérification des droits
        if not session.get('username') or not session.get('rights') or not ('Admin' in session['rights'] or 'SuperAdmin' in session['rights']):
            abort(403)

        language = session.get('language', "EN-en")
        name = request.form.get('name')
        alias = request.form.get('alias')
        type = request.form.get('type')
        rarity = request.form.get('rarity')
        description = request.form.get('description')
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        sjw_sql = SJWSql(cursor)
        character_info = sjw_sql.get_sjw(language)
        sjw_id = character_info['id']
        tag = None

        weapon_sql = SJWWeaponsSql(cursor)
        new_weapon_id = weapon_sql.add_weapon(sjw_id, alias, name, description, type, rarity, tag, language)
        write_log(f"Nouvelle arme ajoutée avec l'ID {new_weapon_id} ({alias})", log_level="INFO")
        
        for evo_idx in range(5):
            evolution_id = request.form.get(f"shadows_evolutions_{evo_idx}_evolution_id")
            if not evolution_id or len(evolution_id) > 10:
                evolution_id = f"A{evo_idx}" if evo_idx != 6 else "A6-10"
            edesc = request.form.get(f'evolution_description_{evo_idx}')
            if evo_idx == 6:
                evo_type = "stat"
                evo_range = "6-10"
                evo_number = None
            else:
                evo_type = "passives"
                evo_range = None
                evo_number = evo_idx
            if evolution_id and edesc:
                weapon_sql.add_evolution(new_weapon_id, evo_number, evolution_id, edesc, evo_type, evo_range, language)
                write_log(f"  - Évolution ajoutée : {evolution_id}", log_level="INFO")

        if not new_weapon_id:
            return "Error adding weapon", 500
        
        sql_manager.conn.commit()
        sql_manager.close()
        
        write_log(f"Arme {new_weapon_id} ({alias}) ajoutée avec succès", log_level="INFO")
        return redirect(url_for('weapon_details', weaponAlias=alias))
    
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
    
    @app.route('/SJW/add_skill/check_image_folder_skill')
    @login_required
    def check_image_folder_skill():
        type = request.args.get('type', '')
        order = request.args.get('order', '')
        folder_name = f"{order}_{type}"
        if type == 'Skill':
            folder_type = 'Skills'
        if type == 'QTE':
            folder_type = 'QTE'
        if type == 'Ultime':
            folder_type = 'Ultime'
        folder_path = os.path.join(
            'static', 'images', 'Sung_Jinwoo', folder_type, folder_name
        )
        write_log(f"Vérification de l'existence du dossier : {folder_path}", log_level="INFO")
        exists = os.path.isdir(folder_path)
        return jsonify({'exists': exists, 'folder': folder_name})

    @app.route('/SJW/add_sjw_skill', methods=['POST'])
    @login_required
    def add_sjw_skill():
        write_log("Tentative d'ajout d'un nouveau skill SJW", log_level="INFO")
        # Vérification des droits
        if not session.get('username') or not session.get('rights') or not ('Admin' in session['rights'] or 'SuperAdmin' in session['rights']):
            abort(403)

        language = session.get('language', "EN-en")
        name = request.form.get('name')
        type = request.form.get('type')
        order = request.form.get('order')
        image = request.form.get('image')
        description = request.form.get('description')

        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        sjw_sql = SJWSql(cursor)
        skills_sql = SJWSkillsSql(cursor)

        # Récupère l'id du SJW
        character_info = sjw_sql.get_sjw(language)
        sjw_id = character_info['id']

        # Ajoute le skill principal
        skill_id = skills_sql.add_skill(
            sjw_id=sjw_id,
            type=type,
            order=order,
            image=image
        )
        # Ajoute la traduction du skill
        skills_sql.add_skill_translation(
            skill_id=skill_id,
            language=language,
            name=name,
            description=description
        )

        # Ajout des gems si présentes (via SJWSkillsSql)
        for i in range(4):
            prefix = f"gems[{i}]"
            if f"{prefix}[type]" in request.form:
                gem_type = request.form.get(f"{prefix}[type]")
                gem_alias = request.form.get(f"{prefix}[alias]")
                gem_image = request.form.get(f"{prefix}[image]")
                gem_order = request.form.get(f"{prefix}[order]")
                gem_name = request.form.get(f"{prefix}[name]")
                gem_description = request.form.get(f"{prefix}[description]")
                gem_break = request.form.get(f"{prefix}[break]") == "on"
                # Ajout gem principale via SJWSkillsSql
                gem_id = skills_sql.add_skill_gem(
                    skill_id=skill_id,
                    type=gem_type,
                    alias=gem_alias,
                    image=gem_image,
                    order=gem_order
                )
                # Traduction gem
                skills_sql.add_skill_gem_translation(
                    gem_id=gem_id,
                    language=language,
                    name=gem_name,
                    description=gem_description
                )
                # Propriétés gem (break uniquement)
                skills_sql.add_skill_gem_properties(
                    gem_id=gem_id,
                    break_value=gem_break
                )
                # Ajout des buffs multiples
                buff_idx = 0
                while f"{prefix}[buffs][{buff_idx}][name]" in request.form:
                    buff_name = request.form.get(f"{prefix}[buffs][{buff_idx}][name]")
                    buff_image = request.form.get(f"{prefix}[buffs][{buff_idx}][image]")
                    buff_description = request.form.get(f"{prefix}[buffs][{buff_idx}][description]")
                    buff_id = skills_sql.add_skill_gem_buff(gem_id, buff_image)
                    skills_sql.add_skill_gem_buff_translation(buff_id, language, buff_name, buff_description)
                    buff_idx += 1

            # Ajout des debuffs multiples
            debuff_idx = 0
            while f"{prefix}[debuffs][{debuff_idx}][name]" in request.form:
                debuff_name = request.form.get(f"{prefix}[debuffs][{debuff_idx}][name]")
                debuff_image = request.form.get(f"{prefix}[debuffs][{debuff_idx}][image]")
                debuff_description = request.form.get(f"{prefix}[debuffs][{debuff_idx}][description]")
                debuff_id = skills_sql.add_skill_gem_debuff(gem_id, debuff_image)
                skills_sql.add_skill_gem_debuff_translation(debuff_id, language, debuff_name, debuff_description)
                debuff_idx += 1

    sql_manager.conn.commit()
    sql_manager.close()
    write_log(f"Skill SJW ajouté avec succès (id={skill_id})", log_level="INFO")
    return redirect(url_for('inner_SJW'))
    
    @app.route('/SJW/skill_images')
    @login_required
    def skill_images():
        type = request.args.get('type', '').replace('..', '').replace('/', '').replace('\\', '')
        order = request.args.get('order', '').replace('..', '').replace('/', '').replace('\\', '')
        folder_name = f"{order}_{type}"
        if type == 'Skill':
            folder_type = 'Skills'
        if type == 'QTE':
            folder_type = 'QTE'
        if type == 'Ultime':
            folder_type = 'Ultime'
        img_dir = os.path.join('static', 'images', 'Sung_Jinwoo', folder_type, folder_name)
        if not os.path.isdir(img_dir):
            write_log(f"Le dossier d'images n'existe pas : {img_dir}", log_level="WARNING")
            return jsonify([])
        images = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))])
        return jsonify(images)
    
def focus_stats_equal(a, b):
    return set(normalize_focus_stats(a)) == set(normalize_focus_stats(b))