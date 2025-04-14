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
                                # Ajouter le chemin relatif de l'image
                                image_path = f'images/Personnages/{type_folder}/{character_folder}/{file}'
                                images.append(image_path)

        return render_template('characters.html', images=images)