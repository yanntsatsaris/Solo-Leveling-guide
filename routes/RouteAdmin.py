from flask import Blueprint, request, render_template, session, redirect, url_for, abort, flash, jsonify, g
from flask_login import login_required
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.sql_entities.panoplies_sql import PanopliesSql
from static.Controleurs.sql_entities.cores_sql import CoresSql
from static.Controleurs.ControleurImages import (
    allowed_file, is_image_size_allowed, verify_image, save_image, rename_image, get_image_format
)
import glob
import os
import zipfile
import shutil

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def is_admin():
    rights = session.get('rights', [])
    return 'Admin' in rights or 'SuperAdmin' in rights

@admin_bp.route('/panoplie', methods=['GET', 'POST'])
@login_required
def admin_panoplie():
    if not is_admin():
        abort(403)
    write_log("Accès à la gestion des effets de panoplie", log_level="INFO", username=session.get('username'))

    language = session.get('language', 'FR-fr')
    db = g.db
    cursor = db.cursor
    panoplies_sql = PanopliesSql(cursor)
    panoplies = panoplies_sql.get_panoplies(language)

    panoplies_with_img = []
    for p in panoplies:
        panoplie_name = p[0].replace(' ', '_')
        artefact_folder = os.path.join('static', 'images', 'Artefacts', panoplie_name)
        img_path = ""
        images = glob.glob(os.path.join(artefact_folder, "Artefact02_*.webp"))
        if not images:
            images = glob.glob(os.path.join(artefact_folder, "Artefact05_*.webp"))
        if images:
            img_path = '/' + images[0].replace('\\', '/')
        panoplies_with_img.append({
            'name': p[0],
            'display_name': p[2],
            'image': img_path
        })

    return render_template('admin_panoplie.html', panoplies=panoplies_with_img)

@admin_bp.route('/panoplie/api/<panoplie_name>')
@login_required
def api_get_panoplie(panoplie_name):
    if not is_admin():
        abort(403)
    db = g.db
    cursor = db.cursor
    panoplies_sql = PanopliesSql(cursor)
    data = panoplies_sql.get_panoplie_all_languages(panoplie_name)
    return data

@admin_bp.route('/panoplie/<panoplie_name>', methods=['POST'])
@login_required
def admin_edit_panoplie(panoplie_name):
    if not is_admin():
        abort(403)
    db = g.db
    cursor = db.cursor
    panoplies_sql = PanopliesSql(cursor)

    for key, value in request.form.items():
        if key.startswith('display_name_'):
            lang = key.split('_', 2)[2]
            panoplies_sql.update_panoplie_display_name(panoplie_name, lang, value)
        elif key.startswith('effect_'):
            _, lang, pieces = key.split('_', 2)
            value = value.replace('\r\n', '\n').replace('\r', '\n')
            panoplies_sql.update_panoplie_effect(panoplie_name, lang, pieces, value)

    db.conn.commit()
    write_log(f"Panoplie '{panoplie_name}' mise à jour avec succès.", log_level="INFO", username=session.get('username'))
    return redirect(url_for('admin.admin_panoplie'))

@admin_bp.route('/panoplie/<panoplie_name>', methods=['PUT'])
@login_required
def admin_create_panoplie(panoplie_name):
    if not is_admin():
        abort(403)
    db = g.db
    cursor = db.cursor
    panoplies_sql = PanopliesSql(cursor)

    data = request.get_json()
    display_names = data.get('display_names', {})
    effects = data.get('effects', {})

    if panoplies_sql.panoplie_exists(panoplie_name):
        return {"error": "Panoplie already exists"}, 400

    panoplie_id = panoplies_sql.create_panoplie(panoplie_name)
    for lang, display_name in display_names.items():
        panoplies_sql.create_panoplie_translation(panoplie_id, lang, panoplie_name, display_name)
    for lang, lang_effects in effects.items():
        for pieces, effect in lang_effects.items():
            set_bonus_id = panoplies_sql.create_panoplie_set_bonus(panoplie_id, int(pieces))
            panoplies_sql.create_panoplie_set_bonus_translation(set_bonus_id, lang, effect)

    db.conn.commit()
    write_log(f"Panoplie '{panoplie_name}' créée avec succès.", log_level="INFO", username=session.get('username'))
    return {"success": True}, 200

@admin_bp.route('/panoplie/check_image/<panoplie_name>')
@login_required
def check_panoplie_image(panoplie_name):
    if not is_admin():
        abort(403)
    folder = os.path.join('static', 'images', 'Artefacts', panoplie_name.replace(' ', '_'))
    found = False
    for prefix in ['Artefact02_', 'Artefact05_']:
        pattern = os.path.join(folder, f"{prefix}*.webp")
        if glob.glob(pattern):
            found = True
            break
    return jsonify({"exists": found})

@admin_bp.route('/cores', methods=['GET'])
@login_required
def admin_cores():
    if not is_admin():
        abort(403)
    write_log("Accès à la gestion des cores", log_level="INFO", username=session.get('username'))
    language = session.get('language', 'FR-fr')
    db = g.db
    cursor = db.cursor
    cores_sql = CoresSql(cursor)
    cores = cores_sql.get_all_cores(language=language)

    cores_with_img = []
    for core in cores:
        core_name = core['color']
        img_path = f'/static/images/Noyaux/{core_name}{core["number"]}.webp'
        cores_with_img.append({
            'id': core['id'],
            'color': core['color'],
            'number': core['number'],
            'effect_name': core['effect_name'],
            'effect': core['effect'],
            'image': img_path
        })

    return render_template('admin_cores.html', cores=cores_with_img)

@admin_bp.route('/cores/api/<color>/<number>')
@login_required
def api_get_core(color, number):
    if not is_admin():
        abort(403)
    db = g.db
    cursor = db.cursor
    cores_sql = CoresSql(cursor)
    data = {}
    for lang in ['FR-fr', 'EN-en']:
        effect = cores_sql.get_core_effect(color, str(number).zfill(2), lang)
        data[lang] = effect
    return jsonify(data)

@admin_bp.route('/cores/<color>/<number>', methods=['POST'])
@login_required
def admin_edit_core(color, number):
    if not is_admin():
        abort(403)
    db = g.db
    cursor = db.cursor
    cores_sql = CoresSql(cursor)

    for key, value in request.form.items():
        if key.startswith('name_'):
            lang = key.split('_', 1)[1]
            cores_sql.update_core_effect_name(color, str(number).zfill(2), lang, value)
        elif key.startswith('effect_'):
            lang = key.split('_', 1)[1]
            value = value.replace('\r\n', '\n').replace('\r', '\n')
            cores_sql.update_core_effect(color, str(number).zfill(2), lang, value)

    db.conn.commit()
    write_log(f"Core '{color}{str(number).zfill(2)}' modifié avec succès.", log_level="INFO", username=session.get('username'))
    return redirect(url_for('admin.admin_cores'))

@admin_bp.route('/cores/<color>/<number>', methods=['PUT'])
@login_required
def admin_create_core(color, number):
    if not is_admin():
        abort(403)
    db = g.db
    cursor = db.cursor
    cores_sql = CoresSql(cursor)

    data = request.get_json()
    names = data.get('names', {})
    effects = data.get('effects', {})

    if cores_sql.core_exists(color, number):
        return {"error": "Core already exists"}, 400

    core_id = cores_sql.create_core(color, number)
    for lang in ['FR-fr', 'EN-en']:
        cores_sql.create_core_translation(core_id, lang, names.get(lang, ""), effects.get(lang, ""))

    db.conn.commit()
    write_log(f"Core '{color}{number}' créé avec succès.", log_level="INFO", username=session.get('username'))
    return {"success": True}, 200

@admin_bp.route('/upload_panoplie_images', methods=['POST'])
@login_required
def upload_panoplie_images():
    if not is_admin():
        abort(403)
    panoplie_name = request.form.get('panoplie_name')
    if not panoplie_name:
        return "Nom de panoplie manquant", 400

    panoplie_name_raw = panoplie_name.replace(' ', '')
    folder = os.path.join('static', 'images', 'Artefacts', panoplie_name.replace(' ', '_'))
    errors = []
    uploaded = 0

    piece_numbers = {
        "Casque": "01", "Plastron": "02", "Gants": "03", "Bottes": "04",
        "Collier": "05", "Bracelet": "06", "Bague": "07", "Boucle d'oreille": "08"
    }

    for piece, num in piece_numbers.items():
        field_name = f"file_{piece.replace(' ', '_')}"
        file = request.files.get(field_name)
        if file:
            if not allowed_file(file.filename):
                errors.append(f"{file.filename}: extension non autorisée")
                continue
            if not is_image_size_allowed(file.stream):
                errors.append(f"{file.filename}: fichier trop volumineux")
                continue
            try:
                verify_image(file.stream)
                ext = os.path.splitext(file.filename)[1].lower()
                new_filename = f"Artefact{num}_{panoplie_name_raw}{ext}"
                save_image(file.stream, folder, new_filename)
                uploaded += 1
            except Exception as e:
                errors.append(f"{file.filename}: {e}")

    if uploaded == 0:
        return "Aucun fichier reçu", 400
    if errors:
        return "Erreurs lors de l'upload :\n" + "\n".join(errors), 400
    return "Images uploadées et vérifiées", 200

@admin_bp.route('/upload_core_images', methods=['POST'])
@login_required
def upload_core_images():
    if not is_admin():
        abort(403)
    core_color = request.form.get('core_color')
    if not core_color:
        return "Couleur du noyau manquante", 400

    errors = []
    uploaded = 0
    for num in [1, 2, 3]:
        field_name = f"file_{num}"
        file = request.files.get(field_name)
        if file and file.filename:
            if not allowed_file(file.filename):
                errors.append(f"{file.filename}: extension non autorisée")
                continue
            if not is_image_size_allowed(file.stream):
                errors.append(f"{file.filename}: fichier trop volumineux")
                continue
            try:
                verify_image(file.stream)
                ext = ".webp"
                filename = f"{core_color}{str(num).zfill(2)}{ext}"
                folder = os.path.join('static', 'images', 'Noyaux')
                save_image(file.stream, folder, filename)
                uploaded += 1
            except Exception as e:
                errors.append(f"{file.filename}: {e}")

    if uploaded == 0:
        return "Aucun fichier reçu", 400
    if errors:
        return "Erreurs lors de l'upload :\n" + "\n".join(errors), 400
    return "Images uploadées et vérifiées", 200

@admin_bp.route('/upload_character_images_zip', methods=['POST'])
@login_required
def upload_character_images_zip():
    if not is_admin():
        abort(403)
    images_zip = request.files.get('images_zip')
    type_ = request.form.get('type')
    alias = request.form.get('alias')
    rarity = request.form.get('rarity')
    if not images_zip or not type_ or not alias or not rarity:
        return "Données manquantes", 400

    type_folder = type_.replace(" ", "_")
    alias_folder = alias.replace(" ", "_")
    rarity_folder = rarity.replace(" ", "_")
    folder_name = f"{rarity_folder}_{type_folder}_{alias_folder}"
    base_folder = os.path.join('static', 'images', 'Personnages', f"SLA_Personnages_{type_folder}")
    target_folder = os.path.join(base_folder, folder_name)

    os.makedirs(base_folder, exist_ok=True)
    temp_extract = os.path.join("tmp", "extract_zip")
    if os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(images_zip) as zf:
        zf.extractall(temp_extract)

    subfolders = [f for f in os.listdir(temp_extract) if os.path.isdir(os.path.join(temp_extract, f))]
    if subfolders:
        src_folder = os.path.join(temp_extract, subfolders[0])
        if subfolders[0] != folder_name:
            os.rename(src_folder, os.path.join(temp_extract, folder_name))
            src_folder = os.path.join(temp_extract, folder_name)
        shutil.move(src_folder, target_folder)
    else:
        os.makedirs(target_folder, exist_ok=True)
        for fname in os.listdir(temp_extract):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                if not fname.startswith(f"{type_folder}_{alias_folder}_"):
                    shutil.rmtree(temp_extract)
                    return f"Image '{fname}' doit commencer par '{type_folder}_{alias_folder}_'", 400
                shutil.move(os.path.join(temp_extract, fname), os.path.join(target_folder, fname))
    shutil.rmtree(temp_extract)
    return "Images extraites et placées dans le dossier du personnage.", 200

@admin_bp.route('/upload_shadow_images_zip', methods=['POST'])
@login_required
def upload_shadow_images_zip():
    if not is_admin():
        abort(403)
    images_zip = request.files.get('images_zip')
    alias = request.form.get('alias')
    if not images_zip or not alias:
        return "Données manquantes", 400

    alias_folder = alias.replace(" ", "_")
    folder_name = f"Shadow_{alias_folder}"
    base_folder = os.path.join('static', 'images', 'Sung_Jinwoo', "Shadows")
    target_folder = os.path.join(base_folder, folder_name)

    os.makedirs(base_folder, exist_ok=True)
    temp_extract = os.path.join("tmp", "extract_zip")
    if os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(images_zip) as zf:
        zf.extractall(temp_extract)

    subfolders = [f for f in os.listdir(temp_extract) if os.path.isdir(os.path.join(temp_extract, f))]
    if subfolders:
        src_folder = os.path.join(temp_extract, subfolders[0])
        if subfolders[0] != folder_name:
            os.rename(src_folder, os.path.join(temp_extract, folder_name))
            src_folder = os.path.join(temp_extract, folder_name)
        shutil.move(src_folder, target_folder)
    else:
        os.makedirs(target_folder, exist_ok=True)
        for fname in os.listdir(temp_extract):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                if not fname.startswith(f"{folder_name}_"):
                    shutil.rmtree(temp_extract)
                    return f"Image '{fname}' doit commencer par '{folder_name}_'", 400
                shutil.move(os.path.join(temp_extract, fname), os.path.join(target_folder, fname))
    shutil.rmtree(temp_extract)
    return "Images extraites et placées dans le dossier des ombres.", 200

@admin_bp.route('/upload_weapon_images_zip', methods=['POST'])
@login_required
def upload_weapon_images_zip():
    if not is_admin():
        abort(403)
    images_zip = request.files.get('images_zip')
    alias = request.form.get('alias')
    type = request.form.get('type')
    if not images_zip or not alias:
        return "Données manquantes", 400

    alias_folder = alias.replace(" ", "_")
    folder_name = f"{type}_{alias_folder}"
    base_folder = os.path.join('static', 'images', 'Sung_Jinwoo', "Armes")
    target_folder = os.path.join(base_folder, folder_name)

    os.makedirs(base_folder, exist_ok=True)
    temp_extract = os.path.join("tmp", "extract_zip")
    if os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(images_zip) as zf:
        zf.extractall(temp_extract)

    subfolders = [f for f in os.listdir(temp_extract) if os.path.isdir(os.path.join(temp_extract, f))]
    if subfolders:
        src_folder = os.path.join(temp_extract, subfolders[0])
        if subfolders[0] != folder_name:
            os.rename(src_folder, os.path.join(temp_extract, folder_name))
            src_folder = os.path.join(temp_extract, folder_name)
        shutil.move(src_folder, target_folder)
    else:
        os.makedirs(target_folder, exist_ok=True)
        for fname in os.listdir(temp_extract):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                if not fname.startswith(f"{folder_name}_"):
                    shutil.rmtree(temp_extract)
                    return f"Image '{fname}' doit commencer par '{folder_name}_'", 400
                shutil.move(os.path.join(temp_extract, fname), os.path.join(target_folder, fname))
    shutil.rmtree(temp_extract)
    return "Images extraites et placées dans le dossier des armes.", 200

@admin_bp.route('/upload_sjw_skill_images_zip', methods=['POST'])
@login_required
def upload_sjw_skill_images_zip():
    if not is_admin():
        abort(403)
    images_zip = request.files.get('images_zip')
    order = request.form.get('order')
    type = request.form.get('type')
    if not images_zip or not order or not type:
        return "Données manquantes", 400

    if type == 'Skill':
        folder_name = f"{order}_Skill"
        prefix = f"{order}_Skill"
        type_folder = 'Skills'
    elif type == 'QTE':
        folder_name = f"{order}_QTE"
        prefix = f"{order}_QTE"
        type_folder = 'QTE'
    elif type == 'Ultime':
        folder_name = f"{order}_Ultime"
        prefix = f"{order}_Ultime"
        type_folder = 'Ultime'
    else:
        return "Type de skill invalide", 400

    base_folder = os.path.join('static', 'images', 'Sung_Jinwoo', type_folder)
    target_folder = os.path.join(base_folder, folder_name)

    os.makedirs(base_folder, exist_ok=True)
    temp_extract = os.path.join("tmp", "extract_zip")
    if os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(images_zip) as zf:
        zf.extractall(temp_extract)

    subfolders = [f for f in os.listdir(temp_extract) if os.path.isdir(os.path.join(temp_extract, f))]
    if subfolders:
        src_folder = os.path.join(temp_extract, subfolders[0])
        if subfolders[0] != folder_name:
            os.rename(src_folder, os.path.join(temp_extract, folder_name))
            src_folder = os.path.join(temp_extract, folder_name)
        shutil.move(src_folder, target_folder)
    else:
        os.makedirs(target_folder, exist_ok=True)
        for fname in os.listdir(temp_extract):
            if fname.lower().endswith('.webp'):
                if fname.startswith(prefix):
                    shutil.move(os.path.join(temp_extract, fname), os.path.join(target_folder, fname))
                    continue
                import re
                gem_pattern = None
                if type == 'Skill':
                    gem_pattern = re.compile(rf"^{order}_(Water|Fire|Light|Dark|Wind)_Skill.*\.webp$", re.IGNORECASE)
                elif type == 'QTE':
                    gem_pattern = re.compile(rf"^{order}_(Water|Fire|Light|Dark|Wind)_QTE.*\.webp$", re.IGNORECASE)
                elif type == 'Ultime':
                    gem_pattern = re.compile(rf"^{order}_(Water|Fire|Light|Dark|Wind)_Ultime.*\.webp$", re.IGNORECASE)
                if gem_pattern and gem_pattern.match(fname):
                    shutil.move(os.path.join(temp_extract, fname), os.path.join(target_folder, fname))
                    continue
                shutil.rmtree(temp_extract)
                return f"L'image '{fname}' doit commencer par '{prefix}' ou respecter le format gem : {order}_Type_{type}*.webp", 400
    shutil.rmtree(temp_extract)
    return f"Images extraites et placées dans le dossier {type_folder}/{folder_name}.", 200
