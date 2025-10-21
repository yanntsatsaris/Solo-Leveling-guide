from flask import Blueprint, request, render_template, session, redirect, url_for, abort, flash, jsonify, current_app
from flask_login import login_required
from app import get_db
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
    db = get_db()
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
    db = get_db()
    cursor = db.cursor
    panoplies_sql = PanopliesSql(cursor)
    data = panoplies_sql.get_panoplie_all_languages(panoplie_name)
    return data

@admin_bp.route('/panoplie/<panoplie_name>', methods=['POST'])
@login_required
def admin_edit_panoplie(panoplie_name):
    if not is_admin():
        abort(403)
    db = get_db()
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
    db = get_db()
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
    db = get_db()
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
    db = get_db()
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
    db = get_db()
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
    db = get_db()
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
