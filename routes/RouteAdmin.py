from flask import request, render_template, session, redirect, url_for, abort, flash, jsonify
from flask_login import login_required
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.sql_entities.panoplies_sql import PanopliesSql
from static.Controleurs.sql_entities.cores_sql import CoresSql
from static.Controleurs.ControleurSql import ControleurSql
from static.Controleurs.ControleurImages import (
    allowed_file, is_image_size_allowed, verify_image, save_image, rename_image, get_image_format
)
import glob
import os
import zipfile
import shutil

def is_admin():
    rights = session.get('rights', [])
    return 'Admin' in rights or 'SuperAdmin' in rights

def admin_routes(app):
    @app.route('/admin/panoplie', methods=['GET', 'POST'])
    @login_required
    def admin_panoplie():
        if not is_admin():
            abort(403)
        write_log("Accès à la gestion des effets de panoplie", log_level="INFO", username=session.get('username'))

        language = session.get('language', 'FR-fr')
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        panoplies_sql = PanopliesSql(cursor)
        panoplies = panoplies_sql.get_panoplies(language)

        # Ajout du chemin image pour chaque panoplie
        panoplies_with_img = []
        for p in panoplies:
            # p[0] = nom interne de la panoplie
            panoplie_name = p[0].replace(' ', '_')
            artefact_folder = os.path.join('static', 'images', 'Artefacts', panoplie_name)
            img_path = ""
            # Cherche Artefact02_*.webp
            images = glob.glob(os.path.join(artefact_folder, "Artefact02_*.webp"))
            if not images:
                # Sinon cherche Artefact05_*.webp
                images = glob.glob(os.path.join(artefact_folder, "Artefact05_*.webp"))
            if images:
                img_path = '/' + images[0].replace('\\', '/')
            panoplies_with_img.append({
                'name': p[0],
                'display_name': p[2],
                'image': img_path
            })

        sql_manager.close()
        return render_template('admin_panoplie.html', panoplies=panoplies_with_img)

    @app.route('/admin/panoplie/api/<panoplie_name>')
    @login_required
    def api_get_panoplie(panoplie_name):
        if not is_admin():
            abort(403)
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        panoplies_sql = PanopliesSql(cursor)
        data = panoplies_sql.get_panoplie_all_languages(panoplie_name)
        sql_manager.close()
        return data

    @app.route('/admin/panoplie/<panoplie_name>', methods=['POST'])
    @login_required
    def admin_edit_panoplie(panoplie_name):
        if not is_admin():
            abort(403)
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        panoplies_sql = PanopliesSql(cursor)

        # Parcours tous les champs du formulaire

        for key, value in request.form.items():
            if key.startswith('display_name_'):
                lang = key.split('_', 2)[2]
                panoplies_sql.update_panoplie_display_name(panoplie_name, lang, value)
            elif key.startswith('effect_'):
                _, lang, pieces = key.split('_', 2)
                # Normalise les retours à la ligne
                value = value.replace('\r\n', '\n').replace('\r', '\n')
                panoplies_sql.update_panoplie_effect(panoplie_name, lang, pieces, value)

        sql_manager.conn.commit()
        sql_manager.close()
        write_log(f"Panoplie '{panoplie_name}' mise à jour avec succès.", log_level="INFO", username=session.get('username'))
        return redirect(url_for('admin_panoplie'))

    @app.route('/admin/panoplie/<panoplie_name>', methods=['PUT'])
    @login_required
    def admin_create_panoplie(panoplie_name):
        if not is_admin():
            abort(403)
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        panoplies_sql = PanopliesSql(cursor)

        # Récupère les données du formulaire (PUT => JSON)
        data = request.get_json()
        display_names = data.get('display_names', {})
        effects = data.get('effects', {})

        # Vérifie si la panoplie existe déjà
        if panoplies_sql.panoplie_exists(panoplie_name):
            sql_manager.close()
            return {"error": "Panoplie already exists"}, 400

        # Création de la panoplie
        panoplie_id = panoplies_sql.create_panoplie(panoplie_name)
        for lang, display_name in display_names.items():
            panoplies_sql.create_panoplie_translation(panoplie_id, lang, panoplie_name, display_name)
        for lang, lang_effects in effects.items():
            for pieces, effect in lang_effects.items():
                set_bonus_id = panoplies_sql.create_panoplie_set_bonus(panoplie_id, int(pieces))
                panoplies_sql.create_panoplie_set_bonus_translation(set_bonus_id, lang, effect)

        sql_manager.conn.commit()
        sql_manager.close()
        write_log(f"Panoplie '{panoplie_name}' créée avec succès.", log_level="INFO", username=session.get('username'))
        return {"success": True}, 200

    @app.route('/admin/panoplie/check_image/<panoplie_name>')
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

    @app.route('/admin/cores', methods=['GET'])
    @login_required
    def admin_cores():
        if not is_admin():
            abort(403)
        write_log("Accès à la gestion des cores", log_level="INFO", username=session.get('username'))
        language = session.get('language', 'FR-fr')
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
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

        sql_manager.close()
        return render_template('admin_cores.html', cores=cores_with_img)

    @app.route('/admin/cores/api/<color>/<number>')
    @login_required
    def api_get_core(color, number):
        if not is_admin():
            abort(403)
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        cores_sql = CoresSql(cursor)
        data = {}
        for lang in ['FR-fr', 'EN-en']:
            effect = cores_sql.get_core_effect(color, str(number).zfill(2), lang)
            data[lang] = effect
        sql_manager.close()
        return jsonify(data)

    @app.route('/admin/cores/<color>/<number>', methods=['POST'])
    @login_required
    def admin_edit_core(color, number):
        if not is_admin():
            abort(403)
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        cores_sql = CoresSql(cursor)

        # Parcours tous les champs du formulaire
        for key, value in request.form.items():
            if key.startswith('name_'):
                lang = key.split('_', 1)[1]
                cores_sql.update_core_effect_name(color, str(number).zfill(2), lang, value)
            elif key.startswith('effect_'):
                lang = key.split('_', 1)[1]
                # Normalise les retours à la ligne
                value = value.replace('\r\n', '\n').replace('\r', '\n')
                cores_sql.update_core_effect(color, str(number).zfill(2), lang, value)

        sql_manager.conn.commit()
        sql_manager.close()
        write_log(
            f"Core '{color}{str(number).zfill(2)}' modifié avec succès.",
            log_level="INFO",
            username=session.get('username')
        )
        return redirect(url_for('admin_cores'))

    @app.route('/admin/cores/<color>/<number>', methods=['PUT'])
    @login_required
    def admin_create_core(color, number):
        if not is_admin():
            abort(403)
        sql_manager = ControleurSql()
        cursor = sql_manager.cursor
        cores_sql = CoresSql(cursor)

        data = request.get_json()
        names = data.get('names', {})
        effects = data.get('effects', {})

        # Vérifie si le core existe déjà
        if cores_sql.core_exists(color, number):
            sql_manager.close()
            return {"error": "Core already exists"}, 400

        # Création du core
        core_id = cores_sql.create_core(color, number)
        for lang in ['FR-fr', 'EN-en']:
            cores_sql.create_core_translation(core_id, lang, names.get(lang, ""), effects.get(lang, ""))

        sql_manager.conn.commit()
        sql_manager.close()
        write_log(f"Core '{color}{number}' créé avec succès.", log_level="INFO", username=session.get('username'))
        return {"success": True}, 200

    @app.route('/admin/upload_panoplie_images', methods=['POST'])
    @login_required
    def upload_panoplie_images():
        if not is_admin():
            abort(403)
        panoplie_name = request.form.get('panoplie_name')
        if not panoplie_name:
            return "Nom de panoplie manquant", 400

        piecesArmure = ["Casque", "Plastron", "Gants", "Bottes"]
        piecesAccessoire = ["Collier", "Bracelet", "Bague", "Boucle d'oreille"]
        allPieces = piecesArmure + piecesAccessoire

        panoplie_name_raw = panoplie_name.replace(' ', '')
        folder = os.path.join('static', 'images', 'Artefacts', panoplie_name.replace(' ', '_'))
        errors = []
        uploaded = 0

        piece_numbers = {
            "Casque": "01",
            "Plastron": "02",
            "Gants": "03",
            "Bottes": "04",
            "Collier": "05",
            "Bracelet": "06",
            "Bague": "07",
            "Boucle d'oreille": "08"
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

    @app.route('/admin/upload_core_images', methods=['POST'])
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
    
    @app.route('admin/upload_character_images_zip', methods=['POST'])
    @login_required
    def upload_images_zip():
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

        # Crée le dossier de type si besoin
        os.makedirs(base_folder, exist_ok=True)

        # Extraction temporaire
        temp_extract = os.path.join("tmp", "extract_zip")
        if os.path.exists(temp_extract):
            shutil.rmtree(temp_extract)
        os.makedirs(temp_extract, exist_ok=True)

        with zipfile.ZipFile(images_zip) as zf:
            zf.extractall(temp_extract)

        # Cherche un dossier dans le zip
        subfolders = [f for f in os.listdir(temp_extract) if os.path.isdir(os.path.join(temp_extract, f))]
        if subfolders:
            # Il y a un dossier, on le renomme si besoin
            src_folder = os.path.join(temp_extract, subfolders[0])
            if subfolders[0] != folder_name:
                os.rename(src_folder, os.path.join(temp_extract, folder_name))
                src_folder = os.path.join(temp_extract, folder_name)
            shutil.move(src_folder, target_folder)
        else:
            # Pas de dossier, on crée le dossier cible et on déplace les images
            os.makedirs(target_folder, exist_ok=True)
            for fname in os.listdir(temp_extract):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    # Vérifie le nom
                    if not fname.startswith(f"{type_folder}_{alias_folder}_"):
                        shutil.rmtree(temp_extract)
                        return f"Image '{fname}' doit commencer par '{type_folder}_{alias_folder}_'", 400
                    shutil.move(os.path.join(temp_extract, fname), os.path.join(target_folder, fname))
        shutil.rmtree(temp_extract)
        return "Images extraites et placées dans le dossier du personnage.", 200