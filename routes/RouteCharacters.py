import os
import json
from flask import Flask, render_template

def characters(app: Flask):
    # Charger les données des personnages depuis le fichier JSON
    with open('data/character.json', 'r') as f:
        characters_data = json.load(f)

    # Charger les données des panoplies
    with open('data/panoplies.json', 'r', encoding='utf-8') as f:
        panoplies_data = json.load(f)

    @app.route('/characters')
    def inner_characters():
        images = []
        character_types = set()  # Utiliser un ensemble pour éviter les doublons

        # Parcourir les données des personnages pour construire les chemins des images
        for character in characters_data:
            type_folder = f"SLA_Personnages_{character['type']}"
            character_folder = character['folder']
            # Utiliser l'alias pour construire le chemin de l'image Codex
            image_path = f'images/Personnages/{type_folder}/{character_folder}/{character["type"]}_{character["alias"]}_Codex.png'
            images.append({
                'path': image_path,
                'name': character['name'],  # Utilisé pour l'affichage
                'alias': character['alias'],  # Utilisé pour les liens
                'type': character['type']  # Ajouter le type pour le filtrage
            })
            # Ajouter le type à l'ensemble
            character_types.add(character['type'])

        # Convertir l'ensemble en liste pour le passer au template
        character_types = sorted(character_types)  # Trier les types pour un affichage cohérent

        return render_template('characters.html', images=images, character_types=character_types)

    @app.route('/characters/<alias>')
    def character_details(alias):
        # Trouver les informations du personnage correspondant
        character_info = next((char for char in characters_data if char['alias'] == alias), None)

        if not character_info:
            return "Character not found", 404

        # Construire le chemin de l'image principale
        type_folder = f"SLA_Personnages_{character_info['type']}"
        character_folder = character_info['folder']
        image_path = f'images/Personnages/{type_folder}/{character_folder}/{character_info["type"]}_{character_info["alias"]}_Personnage.png'

        # Ajouter les informations supplémentaires pour le rendu
        character_info['image'] = image_path
        character_info['description'] = f"{character_info['name']} is a powerful character of type {character_info['type']} in Solo Leveling Arise."

        character_info['background_image'] = f'images/Personnages/{type_folder}/BG_{character_info["type"]}.webp'

        # Construire les chemins des images des passifs
        for passive in character_info.get('passives', []):
            if 'image' in passive:
                passive['image'] = f'images/Personnages/{type_folder}/{character_folder}/{passive["image"]}'
            if 'description' in passive:
                passive['description'] = passive['description'].replace(
                    "src='",
                    f"src='/static/images/Personnages/{type_folder}/{character_folder}/"
                ).replace("\n", "<br>")

        # Construire les chemins des images des skills
        for skill in character_info.get('skills', []):
            if 'image' in skill:
                skill['image'] = f'images/Personnages/{type_folder}/{character_folder}/{skill["image"]}'
            if 'description' in skill:
                skill['description'] = skill['description'].replace(
                    "src='",
                    f"src='/static/images/Personnages/{type_folder}/{character_folder}/"
                ).replace("\n", "<br>")

        # Construire les chemins des images des artefacts
        for artefact in character_info.get('artefacts', []):
            artefact['image'] = f'images/Artefacts/{artefact["image"]}'

        # Construire les chemins des images des noyaux
        for core in character_info.get('cores', []):
            core['image'] = f'images/Noyaux/{core["image"]}'

        # Construire les chemins des images des armes
        for weapon in character_info.get('weapon', []):
            if 'image' in weapon:
                weapon['image'] = f'images/Personnages/{type_folder}/{character_folder}/{weapon["image"]}'
            if 'stats' in weapon:
                weapon['stats'] = weapon['stats'].replace(
                    "src='",
                    f"src='/static/images/Personnages/{type_folder}/{character_folder}/"
                ).replace("\n", "<br>")  # Remplace \n par <br> pour l'affichage HTML

        # Ajouter les focus_stats pour les artefacts
        character_info['focus_stats'] = character_info.get('focus_stats', [])

        # Calculer les effets de panoplie activés
        equipped_sets = {}
        for artefact in character_info.get('artefacts', []):
            set_name = artefact.get('set')
            if set_name:
                equipped_sets[set_name] = equipped_sets.get(set_name, 0) + 1

        # Ajouter les effets activés pour chaque panoplie
        active_set_effects = []
        for panoply in panoplies_data['panoplies']:
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

        # Ajouter les effets activés au contexte
        character_info['active_set_effects'] = active_set_effects

        # Ajouter les évolutions au contexte
        evolutions = []
        for evolution in character_info.get('evolutions', []):
            if 'range' in evolution:
                # Si l'évolution a une plage (ex: 06-10)
                description = evolution.get('description', '')
                # Remplacer les chemins des images dans la description
                description = description.replace(
                    "src='",
                    f"src='/static/images/Personnages/{type_folder}/{character_folder}/"
                )
                evolutions.append({
                    'id': evolution['id'],
                    'range': evolution['range'],
                    'type': evolution['type'],
                    'description': description  # Inclure la description modifiée
                })
            else:
                # Si l'évolution est individuelle
                description = evolution.get('description', '')
                # Remplacer les chemins des images dans la description
                description = description.replace(
                    "src='",
                    f"src='/static/images/Personnages/{type_folder}/{character_folder}/"
                ).replace("\n", "<br>")
                evolutions.append({
                    'id': evolution['id'],
                    'number': evolution['number'],
                    'type': evolution['type'],
                    'description': description  # Inclure la description modifiée
                })

        character_info['evolutions'] = evolutions

        return render_template('character_details.html', character=character_info)