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
        image_path = f'images/Personnages/{type_folder}/{character_folder}/{character_info["type"]}_{character_info["alias"]}.png'

        # Ajouter les informations supplémentaires pour le rendu
        character_info['image'] = image_path
        character_info['description'] = f"{character_info['name']} is a powerful character of type {character_info['type']} in Solo Leveling Arise."

        return render_template('character_details.html', character=character_info)