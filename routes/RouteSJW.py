import json
from flask import Flask, render_template , url_for

def update_image_paths(description, base_path):
    """
    Met à jour les chemins des images dans une description en ajoutant un cache-busting.
    """
    if not description:
        return description

    # Remplace les chemins relatifs par des chemins absolus avec cache-busting
    return description.replace(
        "src='",
        f"src='{url_for('static', filename=base_path)}/"
    ).replace("\n", "<br>")

def SJW(app: Flask):
    # Charger les données des personnages depuis le fichier JSON
    with open('data/SJW.json', 'r', encoding='utf-8') as f:
        characters_data = json.load(f)

    # Charger les données des panoplies
    with open('data/panoplies.json', 'r', encoding='utf-8') as f:
        panoplies_data = json.load(f)
        
    @app.route('/SJW')
    def inner_SJW():
        # Trouver les informations du personnage correspondant
        character_info = next((char for char in characters_data if char['alias'] == "SJW"), None)

        if not character_info:
            return "Character not found", 404

        # Construire le chemin de l'image principale
        character_folder = character_info['folder']
        image_path = f'static/images/{character_folder}/Sung_Jinwoo.png'

        # Ajouter les informations supplémentaires pour le rendu
        character_info['image'] = image_path
        character_info['description'] = f"{character_info['name']} is a powerful character in Solo Leveling Arise."

        # Renvoyer le template avec les données du personnage
        return render_template('SJW.html', character=character_info)