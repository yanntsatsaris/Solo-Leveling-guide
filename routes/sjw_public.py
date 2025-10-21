import json
import os
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
from routes.utils import *

def sjw_public_routes(app: Flask):
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
