import json
import os  # Importer le module os pour vérifier l'existence des fichiers
from flask import Flask, render_template, url_for, session

def update_image_paths(description, base_path):
    """
    Met à jour les chemins des images dans une description en ajoutant un cache-busting.
    """
    if not description:
        return description

    # Vérifiez si le chemin commence déjà par le chemin de base
    updated_description = description
    if f"src='{url_for('static', filename=base_path)}/" not in description:
        updated_description = description.replace(
            "src='",
            f"src='{url_for('static', filename=base_path)}/"
        )

    return updated_description.replace("\n", "<br>")

def characters(app: Flask):
    @app.route('/characters')
    def inner_characters():
        # Récupérer la langue sélectionnée
        language = session.get('language', 'EN-en')

        # Charger les données des personnages depuis le fichier JSON
        with open('data/character.json', 'r', encoding='utf-8') as f:
            characters_data = json.load(f)

        # Charger les données des panoplies depuis le fichier JSON
        with open('data/panoplies.json', 'r', encoding='utf-8') as f:
            panoplies_data = json.load(f)

        # Filtrer les données en fonction de la langue
        characters_data = characters_data.get(language, [])
        panoplies_data = panoplies_data.get(language, [])

        images = []
        character_types = set()

        for character in characters_data:
            type_folder = f"SLA_Personnages_{character['type']}"
            character_folder = character['folder']

            # Construire les chemins possibles pour les images Codex
            base_path = f'static/images/Personnages/{type_folder}/{character_folder}'
            codex_png = f'{base_path}/{character["type"]}_{character["alias"]}_Codex.png'
            codex_webp = f'{base_path}/{character["type"]}_{character["alias"]}_Codex.webp'

            # Vérifier si le fichier .webp existe, sinon utiliser .png
            if os.path.exists(codex_webp):
                image_path = codex_webp.replace('static/', '')
            else:
                image_path = codex_png.replace('static/', '')

            images.append({
                'path': image_path,
                'name': character['name'],
                'alias': character['alias'],
                'type': character['type']
            })
            character_types.add(character['type'])

        character_types = sorted(character_types)

        return render_template(
            'characters.html',
            images=images,
            character_types=character_types,
            panoplies=panoplies_data
        )

    @app.route('/characters/<alias>')
    def character_details(alias):
        # Récupérer la langue sélectionnée
        language = session.get('language', 'EN-en')

        # Charger les données des personnages depuis le fichier JSON
        with open('data/character.json', 'r', encoding='utf-8') as f:
            characters_data = json.load(f)

        # Charger les données des panoplies depuis le fichier JSON
        with open('data/panoplies.json', 'r', encoding='utf-8') as f:
            panoplies_data = json.load(f)

        # Filtrer les données en fonction de la langue
        characters_data = characters_data.get(language, [])
        panoplies_data = panoplies_data.get(language, [])

        # Trouver les informations du personnage correspondant
        character_info = next((char for char in characters_data if char['alias'] == alias), None)

        if not character_info:
            return "Character not found", 404

        # Construire les chemins possibles pour l'image principale (_Personnage)
        type_folder = f"SLA_Personnages_{character_info['type']}"
        character_folder = character_info['folder']
        personnage_png = f'static/images/Personnages/{type_folder}/{character_folder}/{character_info["type"]}_{character_info["alias"]}_Personnage.png'
        personnage_webp = f'static/images/Personnages/{type_folder}/{character_folder}/{character_info["type"]}_{character_info["alias"]}_Personnage.webp'

        # Vérifier si le fichier .webp existe, sinon utiliser .png
        if os.path.exists(personnage_webp):
            image_path = personnage_webp.replace('static/', '')  # Retirer "static/" pour Flask
        else:
            image_path = personnage_png.replace('static/', '')

        # Ajouter les informations supplémentaires pour le rendu
        character_info['image'] = image_path
        character_info['description'] = f"{character_info['name']} is a powerful character of type {character_info['type']} in Solo Leveling Arise."

        character_info['background_image'] = f'images/Personnages/{type_folder}/BG_{character_info["type"]}.webp'

        # Mettre à jour les descriptions des passifs
        for passive in character_info.get('passives', []):
            if 'image' in passive:
                if not passive['image'].startswith('images/'):
                    # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                    passive['image'] = f'images/Personnages/{type_folder}/{character_folder}/{passive["image"]}'
            if 'description' in passive:
                passive['description'] = update_image_paths(passive['description'], f'images/Personnages/{type_folder}/{character_folder}')

        # Mettre à jour les descriptions des skills
        for skill in character_info.get('skills', []):
            if 'image' in skill:
                if not skill['image'].startswith('images/'):
                    # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                    skill['image'] = f'images/Personnages/{type_folder}/{character_folder}/{skill["image"]}'
            if 'description' in skill:
                skill['description'] = update_image_paths(skill['description'], f'images/Personnages/{type_folder}/{character_folder}')

        # Mettre à jour les descriptions des armes
        for weapon in character_info.get('weapon', []):
            if 'image' in weapon:
                if not weapon['image'].startswith('images/'):
                    # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                    weapon['image'] = f'images/Personnages/{type_folder}/{character_folder}/{weapon["image"]}'
            if 'stats' in weapon:
                weapon['stats'] = update_image_paths(weapon['stats'], f'images/Personnages/{type_folder}/{character_folder}')
            # Mettre à jour les évolutions des armes
            for evolution in weapon.get('evolutions', []):
                if 'description' in evolution:
                    evolution['description'] = update_image_paths(evolution['description'], f'images/Personnages/{type_folder}/{character_folder}')

        # Calculer les effets de panoplie activés pour chaque set
        equipment_sets_effects = []
        for equipment_set in character_info.get('equipment_sets', []):
            equipped_sets = {}
            for artefact in equipment_set.get('artefacts', []):
                set_name = artefact.get('set')  # Utiliser le champ 'set' des artefacts
                if set_name:
                    equipped_sets[set_name] = equipped_sets.get(set_name, 0) + 1

            # Ajouter les effets activés pour chaque panoplie
            active_set_effects = []
            for panoply in panoplies_data:
                set_name = panoply['name']
                if set_name in equipped_sets:
                    pieces_equipped = equipped_sets[set_name]
                    for bonus in panoply['set_bonus']:
                        if pieces_equipped >= bonus['pieces_required']:
                            active_set_effects.append({
                                'set_name': set_name,
                                'pieces_required': bonus['pieces_required'],
                                'effect': bonus['effect']
                            })

            equipment_sets_effects.append(active_set_effects)

        # Ajouter les effets activés pour chaque set au contexte
        character_info['equipment_sets_effects'] = equipment_sets_effects

        # Ajouter les évolutions au contexte
        evolutions = []
        for evolution in character_info.get('evolutions', []):
            description = evolution.get('description', '')
            description = update_image_paths(description, f'images/Personnages/{type_folder}/{character_folder}')
            evolution['description'] = description
            evolutions.append(evolution)

        character_info['evolutions'] = evolutions

        # Mettre à jour les données des sets d'équipement
        for equipment_set in character_info.get('equipment_sets', []):
            # Mettre à jour les focus_stats
            equipment_set['focus_stats'] = equipment_set.get('focus_stats', [])

            # Mettre à jour les images des artefacts
            for artefact in equipment_set.get('artefacts', []):
                if 'image' in artefact:
                    if not artefact['image'].startswith('images/'):
                        # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                        artefact['image'] = f'images/Artefacts/{artefact["image"]}'

            # Mettre à jour les images des noyaux
            for core in equipment_set.get('cores', []):
                if 'image' in core:
                    if not core['image'].startswith('images/'):
                        # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                        core['image'] = f'images/Noyaux/{core["image"]}'

        # Renvoyer le template avec les données du personnage
        return render_template('character_details.html', character=character_info)