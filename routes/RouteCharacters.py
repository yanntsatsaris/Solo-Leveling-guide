import json
import os
import re
import unicodedata
import glob
from flask import Flask, render_template, url_for, session, request, redirect, abort, jsonify
from flask_login import login_required, current_user
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
            'background_image': f'images/Personnages/{type_folder}/BG_{char_type}.webp',
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

    @app.route('/characters/edit/<int:char_id>', methods=['POST'])
    @login_required
    def edit_character(char_id):
        # Vérification des droits
        if not session.get('username') or not session.get('rights') or not ('Admin' in session['rights'] or 'SuperAdmin' in session['rights']):
            abort(403)

        language = session.get('language', "EN-en")
        name = request.form.get('name')
        alias = request.form.get('alias')
        description = request.form.get('description')
        rarity = request.form.get('rarity')
        type_ = request.form.get('type')
        char_folder = request.form.get('image_folder')

        sql_manager = ControleurSql()
        cursor = sql_manager.cursor

        characters_sql = CharactersSql(cursor)
        current_character = characters_sql.get_character_full(char_id, language)

        char_modif = False
        if (
            (current_character['name'] or '') != (name or '') or
            current_character['alias'] != alias or
            current_character['type'] != type_ or
            current_character['rarity'] != rarity or
            (current_character['description'] or '') != (description or '')
        ):
            characters_sql.update_character_main(
                char_id=char_id,
                alias=alias,
                type_=type_,
                rarity=rarity,
                name=name,
                description=description,
                language=language
            )
            char_modif = True
            write_log(f"Modification personnage {char_id} ({alias})", log_level="INFO")

        # --- Passifs ---
        passives_sql = PassivesSql(cursor)
        current_passives = passives_sql.get_passives_full(char_id, language)
        existing_passives = [str(p['id']) for p in current_passives]
        form_passive_ids = []
        passif_modif = False
        i = 0
        while True:
            pname = request.form.get(f"passive_name_{i}")
            if pname is None:
                break
            pdesc = request.form.get(f"passive_description_{i}")
            ptag = request.form.get(f"passive_tag_{i}")
            pimg = request.form.get(f"passive_image_{i}")
            pprincipal = request.form.get(f"passive_principal_{i}") == "on"
            phidden = request.form.get(f"passive_hidden_{i}") == "on"
            porder = request.form.get(f"passive_order_{i}")
            if porder is None or porder == "":
                porder = i
            # Ajoute l'index à la méthode
            pid = request.form.get(f"passive_id_{i}")
            if pid:
                db_passive = next((p for p in current_passives if str(p['id']) == str(pid)), None)
                if db_passive and (
                    (db_passive['name'] or '') != (pname or '') or
                    normalize_text(db_passive['description']) != normalize_text(pdesc) or
                    (db_passive['tag'] or '') != (ptag or '') or
                    (db_passive['image_name'] or '') != (pimg or '') or
                    db_passive['principal'] != pprincipal or
                    db_passive['hidden'] != phidden or
                    db_passive['order'] != int(porder)
                ):
                    passives_sql.update_passive(pid, pname, pdesc, ptag, pimg, pprincipal, phidden, language, int(porder))
                    passif_modif = True
                    write_log(f"Modification passif {pid} du personnage {char_id}", log_level="INFO")
                form_passive_ids.append(pid)
            else:
                new_id = passives_sql.add_passive(char_id, pname, pdesc, ptag, pimg, pprincipal, phidden, language, int(porder))
                passif_modif = True
                write_log(f"Ajout passif {new_id} au personnage {char_id}", log_level="INFO")
                form_passive_ids.append(new_id)
            i += 1
        for db_id in existing_passives:
            if str(db_id) not in form_passive_ids:
                passives_sql.delete_passive(db_id)
                passif_modif = True
                write_log(f"Suppression passif {db_id} du personnage {char_id}", log_level="INFO")

        # --- Skills ---
        skills_sql = SkillsSql(cursor)
        current_skills = skills_sql.get_skills_full(char_id, language)
        existing_skills = [str(s['id']) for s in current_skills]
        form_skill_ids = []
        skill_modif = False
        i = 0
        while True:
            sname = request.form.get(f"skill_name_{i}")
            if sname is None:
                break
            sdesc = request.form.get(f"skill_description_{i}")
            stag = request.form.get(f"skill_tag_{i}")
            simg = request.form.get(f"skill_image_{i}")
            sprincipal = request.form.get(f"skill_principal_{i}") == "on"
            sorder = request.form.get(f"skill_order_{i}")
            if sorder is None or sorder == "":
                sorder = i
            sid = request.form.get(f"skill_id_{i}")
            if sid:
                db_skill = next((s for s in current_skills if str(s['id']) == str(sid)), None)
                if db_skill and (
                    (db_skill['name'] or '') != (sname or '') or
                    normalize_text(db_skill['description']) != normalize_text(sdesc) or
                    (db_skill['tag'] or '') != (stag or '') or
                    (db_skill['image_name'] or '') != (simg or '') or
                    db_skill['principal'] != sprincipal or
                    db_skill['order'] != int(sorder)
                ):
                    skills_sql.update_skill(int(sid), sname, sdesc, stag, simg, sprincipal, language, int(sorder))
                    skill_modif = True
                    write_log(f"Modification skill {sid} du personnage {char_id}", log_level="INFO")
                form_skill_ids.append(sid)
            else:
                new_id = skills_sql.add_skill(char_id, sname, sdesc, stag, simg, sprincipal, language, int(sorder))
                skill_modif = True
                write_log(f"Ajout skill {new_id} au personnage {char_id}", log_level="INFO")
                form_skill_ids.append(new_id)
            i += 1
        for db_id in existing_skills:
            if str(db_id) not in form_skill_ids:
                skills_sql.delete_skill(db_id)
                skill_modif = True
                write_log(f"Suppression skill {db_id} du personnage {char_id}", log_level="INFO")

        # --- Armes ---
        weapons_sql = WeaponsSql(cursor)
        current_weapons = weapons_sql.get_weapons_full(char_id, language)
        existing_weapon_ids = [str(w['id']) for w in current_weapons]
        form_weapon_ids = []
        weapon_modif = False
        weapon_idx = 0
       
        while True:
            wname = request.form.get(f"weapon_name_{weapon_idx}")
            if wname is None:
                break
            wstats = request.form.get(f"weapon_stats_{weapon_idx}")
            wtag = request.form.get(f"weapon_tag_{weapon_idx}")
            # Recherche automatique de l'image
            folder = os.path.join('static', 'images', 'Personnages', f"SLA_Personnages_{type_}", char_folder)
            write_log(f"Recherche image arme dans le dossier : {folder}", log_level="INFO")
            pattern = os.path.join(folder, f"{rarity}_{type_}_{alias}_Weapon.*")
            write_log(f"Pattern de recherche : {pattern}", log_level="INFO")
            found_images = glob.glob(pattern)
            write_log(f"Images trouvées : {found_images}", log_level="INFO")
            if found_images:
                wimg = os.path.basename(found_images[0])
            else:
                wimg = ""
            # wimg = request.form.get(f"weapon_image_{weapon_idx}")
            wid = request.form.get(f"weapon_id_{weapon_idx}")
            if wid:
                db_weapon = next((w for w in current_weapons if str(w['id']) == str(wid)), None)
                if db_weapon and (
                    (db_weapon['name'] or '') != (wname or '') or
                    ((normalize_text(db_weapon['stats']) or '') != (normalize_text(wstats) or '')) or
                    (db_weapon['tag'] or '') != (wtag or '') 
                    #(db_weapon['image_name'] or '') != (wimg or '')
                ):
                    write_log(f"Recherche image arme : {wimg}", log_level="INFO")
                    weapons_sql.update_weapon(wid, wname, wstats, wtag, wimg, language)
                    weapon_modif = True
                    write_log(f"Modification arme {wid} du personnage {char_id}", log_level="INFO")
                form_weapon_ids.append(wid)
            else:
                wid = weapons_sql.add_weapon(char_id, wname, wstats, wtag, wimg, language)
                weapon_modif = True
                write_log(f"Ajout arme {wid} au personnage {char_id}", log_level="INFO")
                form_weapon_ids.append(wid)
                db_weapon = None
                current_evos = []
            # --- Evolutions de l'arme ---
            current_evos = db_weapon['evolutions'] if wid and db_weapon and 'evolutions' in db_weapon else []
            existing_evo_ids = [str(e['id']) for e in current_evos]
            form_evo_ids = []
            for evo_idx in range(7):
                evolution_id = request.form.get(f"weapon_evolutions_{weapon_idx}_{evo_idx}_evolution_id")
                if not evolution_id or len(evolution_id) > 10:
                    evolution_id = f"A{evo_idx}" if evo_idx != 6 else "A6-10"
                edesc = request.form.get(f"weapon_evolution_description_{weapon_idx}_{evo_idx}")
                eid = request.form.get(f"weapon_evolutions_id_{weapon_idx}_{evo_idx}")

                # Définition du type et du range selon la position
                if evo_idx == 6:
                    evo_type = "stat"
                    evo_range = "6-10"
                    evo_number = None
                else:
                    evo_type = "passives"
                    evo_range = None
                    evo_number = evo_idx

                db_evo = next((e for e in current_evos if str(e['id']) == str(eid)), None) if eid else None
                if eid:
                    if db_evo and (
                        normalize_text(db_evo['description']) != normalize_text(edesc) or
                        (db_evo['evolution_id'] or '') != (evolution_id or '') or
                        (db_evo.get('type') or '') != (evo_type or '') or
                        (db_evo.get('range') or '') != (evo_range or '')
                    ):
                        weapons_sql.update_weapon_evolution(eid, wid, evo_number, evolution_id, edesc, evo_type, evo_range, language)
                        weapon_modif = True
                        write_log(f"Modification évolution arme {eid} de l'arme {wid}", log_level="INFO")
                    form_evo_ids.append(eid)
                else:
                    new_eid = weapons_sql.add_weapon_evolution(wid, evo_number, evolution_id, edesc, evo_type, evo_range, language)
                    weapon_modif = True
                    write_log(f"Ajout évolution arme {new_eid} à l'arme {wid}", log_level="INFO")
                    form_evo_ids.append(new_eid)
            for db_id in existing_evo_ids:
                if str(db_id) not in form_evo_ids:
                    weapons_sql.delete_weapon_evolution(db_id)
                    weapon_modif = True
                    write_log(f"Suppression évolution arme {db_id} de l'arme {wid}", log_level="INFO")
            weapon_idx += 1  # <-- Correction : à l'intérieur de la boucle
        for db_id in existing_weapon_ids:
            if str(db_id) not in form_weapon_ids:
                weapons_sql.delete_weapon(db_id)
                weapon_modif = True
                write_log(f"Suppression arme {db_id} du personnage {char_id}", log_level="INFO")

        # --- Evolutions du personnage ---
        evolutions_sql = EvolutionsSql(cursor)
        current_evos = evolutions_sql.get_evolutions_full(char_id, language)
        evo_modif = False
        for evo_idx in range(7):
            evolution_id = request.form.get(f"character_evolutions_{evo_idx}_evolution_id")
            if not evolution_id or len(evolution_id) > 10:
                evolution_id = f"A{evo_idx}" if evo_idx != 6 else "A6-10"
            edesc = request.form.get(f"character_evolution_description_{evo_idx}")
            eid = request.form.get(f"character_evolutions_id_{evo_idx}")

            # Définition du type et du range selon la position
            if evo_idx == 6:
                evo_type = "stat"
                evo_range = "6-10"
                evo_number = None
            else:
                evo_type = "passives"
                evo_range = None
                evo_number = evo_idx

            db_evo = next((e for e in current_evos if str(e['id']) == str(eid)), None) if eid else None
            if eid:
                if db_evo and (
                    (db_evo['evolution_id'] or '') != (evolution_id or '') or
                    normalize_text(db_evo['description']) != normalize_text(edesc) or
                    (db_evo.get('type') or '') != (evo_type or '') or
                    (db_evo.get('range') or '') != (evo_range or '')
                ):
                    evolutions_sql.update_evolution(eid, char_id, evo_number, evolution_id, edesc, evo_type, evo_range, language)
                    evo_modif = True
                    write_log(f"Modification évolution {eid} du personnage {char_id}", log_level="INFO")
            else:
                evolutions_sql.add_evolution(char_id, evo_number, evolution_id, edesc, evo_type, evo_range, language)
                evo_modif = True
                write_log(f"Ajout évolution {evo_idx} au personnage {char_id}", log_level="INFO")

        # --- Sets d'équipement, artefacts et noyaux ---
        equipment_set_sql = EquipmentSetSql(cursor)
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
        if not (char_modif or passif_modif or skill_modif or weapon_modif or evo_modif or set_modif):
            write_log(f"Aucune modification détectée pour le personnage {char_id}", log_level="INFO")

        return redirect(url_for('character_details', alias=alias))

    @app.route('/characters/add/check_image_folder')
    @login_required
    def check_image_folder():
        type_ = request.args.get('type', '').replace(' ', '_')
        alias = request.args.get('alias', '').replace(' ', '_')
        rarity = request.args.get('rarity', '').replace(' ', '_')
        folder_name = f"{rarity}_{type_}_{alias}"
        folder_path = os.path.join(
            'static', 'images', 'Personnages', f"SLA_Personnages_{type_}", folder_name
        )
        write_log(f"Vérification de l'existence du dossier : {folder_path}", log_level="INFO")
        exists = os.path.isdir(folder_path)
        return jsonify({'exists': exists, 'folder': folder_name})

    @app.route('/characters/add', methods=['POST'])
    @login_required
    def add_character():
        # Vérification des droits
        if not session.get('username') or not session.get('rights') or not ('Admin' in session['rights'] or 'SuperAdmin' in session['rights']):
            abort(403)

        language = session.get('language', "EN-en")
        name = request.form.get('name')
        alias = request.form.get('alias')
        description = request.form.get('description')
        rarity = request.form.get('rarity')
        type_ = request.form.get('type')
        image_folder = request.form.get('image_folder', '')

        sql_manager = ControleurSql()
        cursor = sql_manager.cursor

        characters_sql = CharactersSql(cursor)
        # Ajoute le personnage principal
        char_id = characters_sql.add_character(
            alias=alias,
            type_=type_,
            rarity=rarity,
            name=name,
            description=description,
            folder=image_folder,
            language=language
        )
        write_log(f"Ajout personnage {char_id} ({alias})", log_level="INFO")

        # --- Passifs ---
        passives_sql = PassivesSql(cursor)
        i = 0
        while True:
            pname = request.form.get(f"passive_name_{i}")
            if pname is None:
                break
            pdesc = request.form.get(f"passive_description_{i}")
            ptag = request.form.get(f"passive_tag_{i}")
            pimg = request.form.get(f"passive_image_{i}")
            pprincipal = request.form.get(f"passive_principal_{i}") == "on"
            phidden = request.form.get(f"passive_hidden_{i}") == "on"
            porder = request.form.get(f"passive_order_{i}")
            if porder is None or porder == "":
                porder = i
            passives_sql.add_passive(char_id, pname, pdesc, ptag, pimg, pprincipal, phidden, language, int(porder))
            write_log(f"Ajout passif {pname} au personnage {char_id}", log_level="INFO")
            i += 1

        # --- Skills ---
        skills_sql = SkillsSql(cursor)
        i = 0
        while True:
            sname = request.form.get(f"skill_name_{i}")
            if sname is None:
                break
            sdesc = request.form.get(f"skill_description_{i}")
            stag = request.form.get(f"skill_tag_{i}")
            simg = request.form.get(f"skill_image_{i}")
            sprincipal = request.form.get(f"skill_principal_{i}") == "on"
            sorder = request.form.get(f"skill_order_{i}")
            if sorder is None or sorder == "":
                sorder = i
            skills_sql.add_skill(char_id, sname, sdesc, stag, simg, sprincipal, language, int(sorder))
            write_log(f"Ajout skill {sname} au personnage {char_id}", log_level="INFO")
            i += 1

        # --- Armes ---
        weapons_sql = WeaponsSql(cursor)
        weapon_idx = 0
        while True:
            wname = request.form.get(f"weapon_name_{weapon_idx}")
            if wname is None:
                break
            wstats = request.form.get(f"weapon_stats_{weapon_idx}")
            wtag = request.form.get(f"weapon_tag_{weapon_idx}")
            # Recherche automatique de l'image
            folder = os.path.join('static', 'images', 'Personnages', f"SLA_Personnages_{type_}", image_folder)
            pattern = os.path.join(folder, f"{rarity}_{type_}_Weapon.*")
            found_images = glob.glob(pattern)
            if found_images:
                wimg = os.path.basename(found_images[0])
            else:
                wimg = ""
            # wimg = request.form.get(f"weapon_image_{weapon_idx}")
            wid = weapons_sql.add_weapon(char_id, wname, wstats, wtag, wimg, language)
            write_log(f"Ajout arme {wname} au personnage {char_id}", log_level="INFO")
            # --- Evolutions de l'arme ---
            for evo_idx in range(7):
                evolution_id = request.form.get(f"weapon_evolutions_{weapon_idx}_{evo_idx}_evolution_id")
                if not evolution_id or len(evolution_id) > 10:
                    evolution_id = f"A{evo_idx}" if evo_idx != 6 else "A6-10"
                edesc = request.form.get(f"weapon_evolution_description_{weapon_idx}_{evo_idx}")
                # Définition du type et du range selon la position
                if evo_idx == 6:
                    evo_type = "stat"
                    evo_range = "6-10"
                    evo_number = None
                else:
                    evo_type = "passives"
                    evo_range = None
                    evo_number = evo_idx
                weapons_sql.add_weapon_evolution(wid, evo_number, evolution_id, edesc, evo_type, evo_range, language)
                write_log(f"Ajout évolution {evolution_id} à l'arme {wname}", log_level="INFO")
            weapon_idx += 1

        # --- Evolutions du personnage ---
        evolutions_sql = EvolutionsSql(cursor)
        for evo_idx in range(7):
            evolution_id = request.form.get(f"character_evolutions_{evo_idx}_evolution_id")
            if not evolution_id or len(evolution_id) > 10:
                evolution_id = f"A{evo_idx}" if evo_idx != 6 else "A6-10"
            edesc = request.form.get(f"character_evolution_description_{evo_idx}")
            # Définition du type et du range selon la position
            if evo_idx == 6:
                evo_type = "stat"
                evo_range = "6-10"
                evo_number = None
            else:
                evo_type = "passives"
                evo_range = None
                evo_number = evo_idx
            evolutions_sql.add_evolution(char_id, evo_number, evolution_id, edesc, evo_type, evo_range, language)
            write_log(f"Ajout évolution {evolution_id} au personnage {char_id}", log_level="INFO")

        # --- Sets d'équipement, artefacts et noyaux ---
        equipment_set_sql = EquipmentSetSql(cursor)
        set_idx = 0
        while True:
            set_name = request.form.get(f"eqset_name_{set_idx}")
            if set_name is None:
                break
            set_desc = request.form.get(f"eqset_description_{set_idx}")
            set_focus = request.form.get(f"eqset_focus_stats_{set_idx}")
            set_order = request.form.get(f"eqset_order_{set_idx}")
            set_id = equipment_set_sql.add_equipment_set(char_id, set_name, set_desc, set_focus, set_order, language)
            write_log(f"Ajout set d'équipement {set_name} au personnage {char_id}", log_level="INFO")
            # --- Artefacts du set ---
            for artefact_idx in range(8):
                aname = request.form.get(f"artefact_name_{set_idx}_{artefact_idx}")
                aset = request.form.get(f"artefact_set_{set_idx}_{artefact_idx}")
                amain = request.form.get(f"artefact_main_stat_{set_idx}_{artefact_idx}")
                asec = request.form.get(f"artefact_secondary_stats_{set_idx}_{artefact_idx}")
                # Recherche automatique de l'image
                aset_folder = (aset or '').replace(' ', '_')
                artefact_folder = os.path.join('static', 'images', 'Artefacts', aset_folder)
                pattern = os.path.join(artefact_folder, f"Artefact0{artefact_idx + 1}_*")
                found_images = glob.glob(pattern)
                if found_images:
                    aimg = os.path.basename(found_images[0])
                else:
                    aimg = ""
                equipment_set_sql.add_artefact(set_id, aname, aset, aimg, amain, asec, language)
                write_log(f"Ajout artefact {aname} au set {set_name}", log_level="INFO")
            # --- Noyaux du set ---
            for core_idx in range(3):
                cname = request.form.get(f"core_name_{set_idx}_{core_idx}")
                cmain = request.form.get(f"core_main_stat_{set_idx}_{core_idx}")
                csec = request.form.get(f"core_secondary_stat_{set_idx}_{core_idx}")
                cnumber = f"{core_idx+1:02d}"
                cimg = cname + cnumber + ".webp"
                equipment_set_sql.add_core(set_id, cname, cimg, cmain, csec, cnumber, language)
                write_log(f"Ajout noyau {cname} au set {set_name}", log_level="INFO")
            set_idx += 1

        sql_manager.conn.commit()
        sql_manager.close()

        write_log(f"Ajout complet du personnage {char_id} ({alias})", log_level="INFO")
        return redirect(url_for('character_details', alias=alias))

    @app.route('/characters/images_for/<type_folder>/<folder>')
    @login_required
    def images_for_character(type_folder, folder):
        # Sécurise les noms
        type_folder = type_folder.replace('..', '').replace('/', '').replace('\\', '')
        folder = folder.replace('..', '').replace('/', '').replace('\\', '')
        img_dir = os.path.join('static', 'images', 'Personnages', f'SLA_Personnages_{type_folder}', folder)
        if not os.path.isdir(img_dir):
            write_log(f"Le dossier d'images n'existe pas : {img_dir}", log_level="WARNING")
            return jsonify([])
        images = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))])
        return jsonify(images)

def focus_stats_equal(a, b):
    return set(normalize_focus_stats(a)) == set(normalize_focus_stats(b))