import os
import glob
from flask import Blueprint, render_template, url_for, session, current_app, g
from app import cache
from static.Controleurs.ControleurLog import write_log
from static.Controleurs.sql_entities.characters_sql import CharactersSql
from static.Controleurs.sql_entities.panoplies_sql import PanopliesSql
from static.Controleurs.sql_entities.characters.passives_sql import PassivesSql
from static.Controleurs.sql_entities.characters.evolutions_sql import EvolutionsSql
from static.Controleurs.sql_entities.characters.skills_sql import SkillsSql
from static.Controleurs.sql_entities.characters.weapons_sql import WeaponsSql
from static.Controleurs.sql_entities.characters.equipment_set_sql import EquipmentSetSql
from static.Controleurs.sql_entities.cores_sql import CoresSql
from routes.utils import process_description

characters_public_bp = Blueprint('characters_public', __name__)

@characters_public_bp.route('/characters')
@cache.cached(timeout=3600, key_prefix='characters_list_%s')
def inner_characters():
    language = session.get('language', "EN-en")
    if not language:
        return "Language not set", 400

    db = g.db
    characters_sql = CharactersSql(db.cursor)
    characters_data = characters_sql.get_characters(language)
    panoplies_sql = PanopliesSql(db.cursor)
    cores_sql = CoresSql(db.cursor)

    panoplies_effects = panoplies_sql.get_panoplies_effects(language)
    panoplies_names = sorted(list({p['set_name'] for p in panoplies_effects}))
    cores_effects = cores_sql.get_cores_effects(language)
    cores_names = sorted(list({c['color'] for c in cores_effects}))

    images = []
    character_types = set()
    rarities = set()

    for row in characters_data:
        char_id, char_type, char_rarity, char_alias, char_folder, char_name = row
        type_folder = f"SLA_Personnages_{char_type}"
        if char_folder is None or char_folder.strip() == "":
            char_folder = f"{char_rarity}_{char_type}_{char_alias}"
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
    rarities = sorted(rarities, reverse=True)

    return render_template(
        'characters.html',
        images=images,
        character_types=character_types,
        rarities=rarities,
        panoplies_list=panoplies_names,
        cores_list=cores_names
    )

@characters_public_bp.route('/characters/<alias>')
@cache.cached(timeout=3600, key_prefix='character_details_%s')
def character_details(alias):
    write_log(f"Accès aux détails du personnage: {alias}", log_level="INFO")
    language = session.get('language', "EN-en")
    if not language:
        return "Language not set", 400

    db = g.db
    characters_sql = CharactersSql(db.cursor)
    passives_sql = PassivesSql(db.cursor)
    evolutions_sql = EvolutionsSql(db.cursor)
    skills_sql = SkillsSql(db.cursor)
    weapons_sql = WeaponsSql(db.cursor)
    equipment_set_sql = EquipmentSetSql(db.cursor)
    panoplies_sql = PanopliesSql(db.cursor)
    cores_sql = CoresSql(db.cursor)

    row = characters_sql.get_character_details(language, alias)
    if not row:
        return "Character not found", 404

    char_id = row['characters_id']
    char_type = row['characters_type']
    char_rarity = row['characters_rarity']
    char_alias = row['characters_alias']
    char_folder = row['characters_folder']
    char_name = row['character_translations_name']
    char_description = row['character_translations_description']

    type_folder = f"SLA_Personnages_{char_type}"
    if char_folder is None or char_folder.strip() == "":
        char_folder = f"{char_rarity}_{char_type}_{char_alias}"
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
        'images_folder' : char_folder
    }

    passives = passives_sql.get_passives(char_id, language, type_folder, char_folder)
    all_passives = passives_sql.get_passives(char_id, language, type_folder, char_folder)

    skills = skills_sql.get_skills(char_id, language, type_folder, char_folder)
    weapons = weapons_sql.get_weapons(char_id, language, type_folder, char_folder)

    all_tags = passives + skills + weapons
    passives = [p for p in passives if not p.get('hidden', False)]

    for passive in passives:
        passive['description_raw'] = passive['description']
        passive['description'] = process_description(passive['description'], all_tags, base_path)
    character_info['passives'] = passives

    for passive in all_passives:
        passive['description_raw'] = passive['description']
        passive['description'] = process_description(passive['description'], all_tags, base_path)
    character_info['passives_all'] = all_passives

    evolutions = evolutions_sql.get_evolutions(char_id, language, type_folder, char_folder)
    for evo in evolutions:
        evo['description_raw'] = evo['description']
        evo['description'] = process_description(evo['description'], all_tags, base_path)
    character_info['evolutions'] = evolutions

    for skill in skills:
        skill['description_raw'] = skill['description']
        skill['description'] = process_description(skill['description'], all_tags, base_path)
    character_info['skills'] = skills

    weapons = weapons_sql.get_weapons(char_id, language, type_folder, char_folder)
    for weapon in weapons:
        weapon['stats_raw'] = weapon.get('stats', '')
        weapon['stats'] = process_description(weapon.get('stats', ''), all_tags, base_path)
        for evo in weapon.get('evolutions', []):
            evo['description_raw'] = evo['description']
            evo['description'] = process_description(evo['description'], all_tags, base_path)
    character_info['weapon'] = weapons

    equipment_sets = []
    for eq_set_id, eq_set_name in equipment_set_sql.get_equipment_sets(char_id, language):
        equipment_sets.append(
            equipment_set_sql.get_equipment_set_details(eq_set_id, eq_set_name, language)
        )
    character_info['equipment_sets'] = equipment_sets
    for eq_set in character_info['equipment_sets']:
        eq_set['description_raw'] = eq_set['description']
        eq_set['description'] = process_description(eq_set['description'], all_tags, base_path)

    for eq_set in character_info['equipment_sets']:
        for core in eq_set['cores']:
            core['color'] = core['name']

    panoplies_effects = panoplies_sql.get_panoplies_effects(language)
    panoplies_names = sorted(list({p['set_name'] for p in panoplies_effects}))
    cores_effects = cores_sql.get_cores_effects(language)
    cores_names = sorted(list({c['color'] for c in cores_effects}))
    if cores_effects is None:
        cores_effects = []

    return render_template(
        'character_details.html',
        character=character_info,
        language=language,
        panoplies_effects=panoplies_effects,
        cores_effects=cores_effects,
        panoplies_list=panoplies_names,
        cores_list=cores_names
    )
