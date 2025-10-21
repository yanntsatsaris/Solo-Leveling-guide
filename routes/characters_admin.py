import os
import glob
from flask import Blueprint, session, request, redirect, abort, jsonify, url_for, current_app
from flask_login import login_required
from app import get_db
from routes.utils import *
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.sql_entities.characters_sql import CharactersSql
from static.Controleurs.sql_entities.characters.passives_sql import PassivesSql
from static.Controleurs.sql_entities.characters.evolutions_sql import EvolutionsSql
from static.Controleurs.sql_entities.characters.skills_sql import SkillsSql
from static.Controleurs.sql_entities.characters.weapons_sql import WeaponsSql
from static.Controleurs.sql_entities.characters.equipment_set_sql import EquipmentSetSql

characters_admin_bp = Blueprint('characters_admin', __name__)

@characters_admin_bp.route('/characters/edit/<int:char_id>', methods=['POST'])
@login_required
def edit_character(char_id):
    if not session.get('username') or not session.get('rights') or not ('Admin' in session['rights'] or 'SuperAdmin' in session['rights']):
        abort(403)

    language = session.get('language', "EN-en")
    name = request.form.get('name')
    alias = request.form.get('alias')
    description = request.form.get('description')
    rarity = request.form.get('rarity')
    type_ = request.form.get('type')
    char_folder = request.form.get('image_folder')

    db = get_db()
    cursor = db.cursor

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
        folder = os.path.join('static', 'images', 'Personnages', f"SLA_Personnages_{type_}", char_folder)
        pattern = os.path.join(folder, f"{type_}_{alias}_Weapon.*")
        found_images = glob.glob(pattern)
        if found_images:
            wimg = os.path.basename(found_images[0])
        else:
            wimg = ""
        wid = request.form.get(f"weapon_id_{weapon_idx}")
        if wid:
            db_weapon = next((w for w in current_weapons if str(w['id']) == str(wid)), None)
            if db_weapon and (
                (db_weapon['name'] or '') != (wname or '') or
                ((normalize_text(db_weapon['stats']) or '') != (normalize_text(wstats) or '')) or
                (db_weapon['tag'] or '') != (wtag or '')
            ):
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
        current_evos = db_weapon['evolutions'] if wid and db_weapon and 'evolutions' in db_weapon else []
        existing_evo_ids = [str(e['id']) for e in current_evos]
        form_evo_ids = []
        for evo_idx in range(7):
            evolution_id = request.form.get(f"weapon_evolutions_{weapon_idx}_{evo_idx}_evolution_id")
            if not evolution_id or len(evolution_id) > 10:
                evolution_id = f"A{evo_idx}" if evo_idx != 6 else "A6-10"
            edesc = request.form.get(f"weapon_evolution_description_{weapon_idx}_{evo_idx}")
            eid = request.form.get(f"weapon_evolutions_id_{weapon_idx}_{evo_idx}")

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
        weapon_idx += 1
    for db_id in existing_weapon_ids:
        if str(db_id) not in form_weapon_ids:
            weapons_sql.delete_weapon(db_id)
            weapon_modif = True
            write_log(f"Suppression arme {db_id} du personnage {char_id}", log_level="INFO")

    evolutions_sql = EvolutionsSql(cursor)
    current_evos = evolutions_sql.get_evolutions_full(char_id, language)
    evo_modif = False
    for evo_idx in range(7):
        evolution_id = request.form.get(f"character_evolutions_{evo_idx}_evolution_id")
        if not evolution_id or len(evolution_id) > 10:
            evolution_id = f"A{evo_idx}" if evo_idx != 6 else "A6-10"
        edesc = request.form.get(f"character_evolution_description_{evo_idx}")
        eid = request.form.get(f"character_evolutions_id_{evo_idx}")

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

        current_artefacts = db_set['artefacts'] if set_id and db_set and 'artefacts' in db_set else []
        existing_artefact_ids = [str(a['id']) for a in current_artefacts]
        form_artefact_ids = []
        for artefact_idx in range(8):
            aname = request.form.get(f"artefact_name_{set_idx}_{artefact_idx}")
            aset = request.form.get(f"artefact_set_{set_idx}_{artefact_idx}")
            amain = request.form.get(f"artefact_main_stat_{set_idx}_{artefact_idx}")
            asec = request.form.get(f"artefact_secondary_stats_{set_idx}_{artefact_idx}")
            aid = request.form.get(f"artefact_id_{set_idx}_{artefact_idx}")

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

        current_cores = db_set['cores'] if set_id and db_set and 'cores' in db_set else []
        existing_core_ids = [str(c['id']) for c in current_cores]
        form_core_ids = []
        for core_idx in range(3):
            cname = request.form.get(f"core_name_{set_idx}_{core_idx}")
            cmain = request.form.get(f"core_main_stat_{set_idx}_{core_idx}")
            csec = request.form.get(f"core_secondary_stat_{set_idx}_{core_idx}")
            cid = request.form.get(f"core_id_{set_idx}_{core_idx}")
            cnumber = f"{core_idx+1:02d}"
            cimg = cname + cnumber + ".webp"
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

    db.conn.commit()

    if not (char_modif or passif_modif or skill_modif or weapon_modif or evo_modif or set_modif):
        write_log(f"Aucune modification détectée pour le personnage {char_id}", log_level="INFO")

    return redirect(url_for('characters_public.character_details', alias=alias))

@characters_admin_bp.route('/characters/add/check_image_folder')
@login_required
def check_image_folder():
    type_ = request.args.get('type', '').replace(' ', '_')
    alias = request.args.get('alias', '').replace(' ', '_')
    rarity = request.args.get('rarity', '').replace(' ', '_')
    folder_name = f"{rarity}_{type_}_{alias}"
    folder_path = os.path.join('static', 'images', 'Personnages', f"SLA_Personnages_{type_}", folder_name)
    write_log(f"Vérification de l'existence du dossier : {folder_path}", log_level="INFO")
    exists = os.path.isdir(folder_path)
    return jsonify({'exists': exists, 'folder': folder_name})

@characters_admin_bp.route('/characters/add', methods=['POST'])
@login_required
def add_character():
    if not session.get('username') or not session.get('rights') or not ('Admin' in session['rights'] or 'SuperAdmin' in session['rights']):
        abort(403)

    language = session.get('language', "EN-en")
    name = request.form.get('name')
    alias = request.form.get('alias')
    description = request.form.get('description')
    rarity = request.form.get('rarity')
    type_ = request.form.get('type')
    image_folder = request.form.get('image_folder', '')
    if image_folder is None or image_folder.strip() == "":
        image_folder = f"{rarity}_{type_}_{alias}"

    db = get_db()
    cursor = db.cursor

    characters_sql = CharactersSql(cursor)
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

    weapons_sql = WeaponsSql(cursor)
    weapon_idx = 0
    while True:
        wname = request.form.get(f"weapon_name_{weapon_idx}")
        if wname is None:
            break
        wstats = request.form.get(f"weapon_stats_{weapon_idx}")
        wtag = request.form.get(f"weapon_tag_{weapon_idx}")
        folder = os.path.join('static', 'images', 'Personnages', f"SLA_Personnages_{type_}", image_folder)
        pattern = os.path.join(folder, f"{rarity}_{type_}_Weapon.*")
        found_images = glob.glob(pattern)
        if found_images:
            wimg = os.path.basename(found_images[0])
        else:
            wimg = ""
        wid = weapons_sql.add_weapon(char_id, wname, wstats, wtag, wimg, language)
        write_log(f"Ajout arme {wname} au personnage {char_id}", log_level="INFO")
        for evo_idx in range(7):
            evolution_id = request.form.get(f"weapon_evolutions_{weapon_idx}_{evo_idx}_evolution_id")
            if not evolution_id or len(evolution_id) > 10:
                evolution_id = f"A{evo_idx}" if evo_idx != 6 else "A6-10"
            edesc = request.form.get(f"weapon_evolution_description_{weapon_idx}_{evo_idx}")
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

    evolutions_sql = EvolutionsSql(cursor)
    for evo_idx in range(7):
        evolution_id = request.form.get(f"character_evolutions_{evo_idx}_evolution_id")
        if not evolution_id or len(evolution_id) > 10:
            evolution_id = f"A{evo_idx}" if evo_idx != 6 else "A6-10"
        edesc = request.form.get(f"character_evolution_description_{evo_idx}")
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
        for artefact_idx in range(8):
            aname = request.form.get(f"artefact_name_{set_idx}_{artefact_idx}")
            aset = request.form.get(f"artefact_set_{set_idx}_{artefact_idx}")
            amain = request.form.get(f"artefact_main_stat_{set_idx}_{artefact_idx}")
            asec = request.form.get(f"artefact_secondary_stats_{set_idx}_{artefact_idx}")
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
        for core_idx in range(3):
            cname = request.form.get(f"core_name_{set_idx}_{core_idx}")
            cmain = request.form.get(f"core_main_stat_{set_idx}_{core_idx}")
            csec = request.form.get(f"core_secondary_stat_{set_idx}_{core_idx}")
            cnumber = f"{core_idx+1:02d}"
            cimg = cname + cnumber + ".webp"
            equipment_set_sql.add_core(set_id, cname, cimg, cmain, csec, cnumber, language)
            write_log(f"Ajout noyau {cname} au set {set_name}", log_level="INFO")
        set_idx += 1

    db.conn.commit()

    write_log(f"Ajout complet du personnage {char_id} ({alias})", log_level="INFO")
    return redirect(url_for('characters_public.character_details', alias=alias))

@characters_admin_bp.route('/characters/images_for/<type_folder>/<folder>')
@login_required
def images_for_character(type_folder, folder):
    type_folder = type_folder.replace('..', '').replace('/', '').replace('\\', '')
    folder = folder.replace('..', '').replace('/', '').replace('\\', '')
    img_dir = os.path.join('static', 'images', 'Personnages', f'SLA_Personnages_{type_folder}', folder)
    if not os.path.isdir(img_dir):
        write_log(f"Le dossier d'images n'existe pas : {img_dir}", log_level="WARNING")
        return jsonify([])
    images = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))])
    return jsonify(images)
