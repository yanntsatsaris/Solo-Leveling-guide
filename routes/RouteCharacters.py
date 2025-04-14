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
                            # Vérifier que le fichier se termine par "_Codex.png" mais pas "_Weapon_Codex.png" ou "_Arme_Codex.png"
                            if file.endswith('_Codex.png') and not ('_Weapon_Codex.png' in file or '_Arme_Codex.png' in file):
                                # Ajouter le chemin relatif de l'image et le nom du personnage
                                character_name = character_folder.split('_')[-1]  # Extraire le nom du personnage
                                images.append({
                                    'path': f'images/Personnages/{type_folder}/{character_folder}/{file}',
                                    'name': character_name
                                })

        return render_template('characters.html', images=images)

    @app.route('/characters/<name>')
    def character_details(name):
        # Exemple de données fictives pour un personnage
        character_info = {
            'name': name,
            'description': f'{name} is a powerful character in Solo Leveling Arise.',
            'image': f'images/Personnages/SLA_Personnages_Type1/SSR_Type1_{name}/Type1_{name}_Codex.png'
        }
        return render_template('character_details.html', character=character_info)