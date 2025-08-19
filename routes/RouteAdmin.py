from flask import request, render_template, session, redirect, url_for, abort, flash
from flask_login import login_required
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.sql_entities.panoplies_sql import PanopliesSql
from static.Controleurs.ControleurSql import ControleurSql
import glob
import os

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

    @app.route('/admin/cores', methods=['GET', 'POST'])
    @login_required
    def admin_cores():
        if not is_admin():
            abort(403)
        write_log("Accès à la gestion des noyaux", log_level="INFO", username=session.get('username'))
        # Ajoute ici la logique pour gérer les noyaux et leurs effets
        if request.method == 'POST':
            # Traitement du formulaire d'ajout/modification de noyau
            pass
        # Récupération des noyaux existants pour affichage
        cores = []  # À remplacer par la récupération réelle
        return render_template('admin_cores.html', cores=cores)

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

        sql_manager.close()
        write_log(f"Panoplie '{panoplie_name}' mise à jour avec succès.", log_level="INFO", username=session.get('username'))
        return redirect(url_for('admin_panoplie'))