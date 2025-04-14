import os
from flask import Flask, render_template

def characters(app: Flask):
    @app.route('/characters')
    def inner_characters():
        # Chemin vers le dossier "personnages"
        base_path = os.path.join(app.static_folder, 'images', 'Personnages')
        images = []

        # Parcourir les sous-dossiers pour trouver les images
        for type_folder in os.listdir(base_path):
            type_path = os.path.join(base_path, type_folder)
            if os.path.isdir(type_path):
                for character_folder in os.listdir(type_path):
                    character_path = os.path.join(type_path, character_folder)
                    if os.path.isdir(character_path):
                        for file in os.listdir(character_path):
                            # Vérifier que le fichier correspond au format "Type_NomPersonnage_Codex.png"
                            if file.endswith('_Codex.png') and not ('_Weapon_Codex.png' in file or '_Arme_Codex.png' in file):
                                character_name = character_folder.split('_')[-1]  # Extraire le nom du personnage
                                images.append({
                                    'path': f'images/Personnages/{type_folder}/{character_folder}/{file}',
                                    'name': character_name
                                })

        return render_template('characters.html', images=images)

    @app.route('/characters/<name>')
    def character_details(name):
        # Chemin vers le dossier "personnages"
        base_path = os.path.join(app.static_folder, 'images', 'Personnages')
        character_image = None
        character_type = None

        # Parcourir les sous-dossiers pour trouver l'image "Type_NomPersonnage.png"
        for type_folder in os.listdir(base_path):
            type_path = os.path.join(base_path, type_folder)
            if os.path.isdir(type_path):
                for character_folder in os.listdir(type_path):
                    if name in character_folder:  # Vérifie si le nom correspond au dossier
                        character_path = os.path.join(type_path, character_folder)
                        if os.path.isdir(character_path):
                            # Construire le nom de l'image attendu
                            type_prefix = type_folder.split('_')[-1]  # Extraire le type du dossier
                            expected_image = f'{type_prefix}_{name}.png'
                            for file in os.listdir(character_path):
                                if file == expected_image:  # Vérifie si le fichier correspond
                                    character_image = f'images/Personnages/{type_folder}/{character_folder}/{file}'
                                    character_type = type_prefix  # Extraire le type
                                    break

        # Exemple de données fictives pour un personnage
        character_info = {
            'name': name,
            'type': character_type,
            'description': f'{name} is a powerful character of type {character_type} in Solo Leveling Arise.',
            'image': character_image
        }
        return render_template('character_details.html', character=character_info)