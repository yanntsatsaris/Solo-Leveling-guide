import os
import json
from flask import Flask, render_template

def characters(app: Flask):
    # Charger les données des personnages depuis le fichier JSON
    with open('data/character.json', 'r') as f:
        characters_data = json.load(f)

    @app.route('/characters')
    def inner_characters():
        images = []

        # Parcourir les données des personnages pour construire les chemins des images
        for character in characters_data:
            type_folder = f"SLA_Personnages_{character['type']}"
            character_folder = character['folder']
            # Utiliser l'alias pour construire le chemin de l'image Codex
            image_path = f'images/Personnages/{type_folder}/{character_folder}/{character["type"]}_{character["alias"]}_Codex.png'
            images.append({
                'path': image_path,
                'name': character['name'],  # Utilisé pour l'affichage
                'alias': character['alias']  # Utilisé pour les liens
            })

        return render_template('characters.html', images=images)

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

        return render_template('character_details.html', character=character_info)