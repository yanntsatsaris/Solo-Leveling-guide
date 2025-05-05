import json
from static.Controleurs.ControleurLog import write_log
from flask import Flask, render_template, session , url_for

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

def SJW(app: Flask):
        
    @app.route('/SJW')
    def inner_SJW():
        # Récupérer la langue sélectionnée ou définir 'EN-en' par défaut
        language = session.get('language', 'EN-en')

        # Charger les données des personnages depuis le fichier JSON
        with open('data/SJW.json', 'r', encoding='utf-8') as f:
            characters_data = json.load(f)

        # Charger les données des panoplies depuis le fichier JSON
        with open('data/panoplies.json', 'r', encoding='utf-8') as f:
            panoplies_data = json.load(f)

        # Filtrer les données en fonction de la langue
        characters_data = characters_data.get(language, [])
        panoplies_data = panoplies_data.get(language, [])
        
        # Trouver les informations du personnage correspondant
        character_info = next((char for char in characters_data if char['alias'] == "SJW"), None)

        if not character_info:
            return "Character not found", 404

        # Construire le chemin de l'image principale
        character_folder = character_info['folder']
        image_path = f'images/{character_folder}/Sung_Jinwoo.png'

        # Ajouter les informations supplémentaires pour le rendu
        character_info['image'] = image_path
        character_info['description'] = f"{character_info['name']} is a powerful character of in Solo Leveling Arise."

        #character_info['background_image'] = f'images/Personnages/{type_folder}/BG_{character_info["type"]}.webp'

        # Mettre à jour les descriptions des passifs
        for passive in character_info.get('passives', []):
            if 'image' in passive:
                if not passive['image'].startswith('images/'):
                    # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                    passive['image'] = f'images/{character_folder}/{passive["image"]}'
            if 'description' in passive:
                passive['description'] = update_image_paths(passive['description'], f'images/{character_folder}')

        # Mettre à jour les descriptions des skills
        for skill in character_info.get('skills', []):
            if 'image' in skill:
                if not skill['image'].startswith('images/'):
                    # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                    skill['image'] = f'images/{character_folder}/{skill["image"]}'
            if 'description' in skill:
                skill['description'] = update_image_paths(skill['description'], f'images/{character_folder}')

        # Récupérer et mettre à jour les données des shadows
        shadows = character_info.get('shadows', [])
        for shadow in shadows:
            if 'image' in shadow:
                if not shadow['image'].startswith('images/'):
                    # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                    shadow['image'] = f'images/{character_folder}/Shadows/{shadow["image"]}'

        character_info['shadows'] = shadows
        
        # Mettre à jour les descriptions des armes
        for weapon in character_info.get('weapon', []):
            if 'image' in weapon:
                # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                if not weapon['image'].startswith('images/'):
                    weapon['image'] = f'images/{character_folder}/Armes/{weapon["folder"]}/{weapon["image"]}'
            if 'codex' in weapon:
                if not weapon['codex'].startswith('images/'):
                    weapon['codex'] = f'images/{character_folder}/Armes/{weapon["folder"]}/{weapon["codex"]}'
            if 'stats' in weapon:
                weapon['stats'] = update_image_paths(weapon['stats'], f'images/{character_folder}')
            # Mettre à jour les évolutions des armes
            for evolution in weapon.get('evolutions', []):
                if 'description' in evolution:
                    evolution['description'] = update_image_paths(evolution['description'], f'images/{character_folder}')

        # Calculer les effets de panoplie activés
        equipped_sets = {}
        for equipment_set in character_info.get('equipment_sets', []):
            for artefact in equipment_set.get('artefacts', []):
                set_name = artefact.get('set')  # Utiliser le champ 'set' des artefacts
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
            description = evolution.get('description', '')
            description = update_image_paths(description, f'images/{character_folder}')
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
                    # Vérifiez si le chemin est déjà absolu pour éviter les doublons
                    if not artefact['image'].startswith('images/'):
                        artefact['image'] = f'images/Artefacts/{artefact["image"]}'

            # Mettre à jour les images des noyaux
            for core in equipment_set.get('cores', []):
                core['image'] = f'images/Noyaux/{core["image"]}'

        # Renvoyer le template avec les données du personnage
        return render_template('SJW.html', character=character_info)

    @app.route('/SJW/shadow/<shadowName>')
    def shadow_details(shadowName):
        # Récupérer la langue sélectionnée ou définir 'EN-en' par défaut
        language = session.get('language', 'EN-en')

        # Charger les données des personnages depuis le fichier JSON
        with open('data/SJW.json', 'r', encoding='utf-8') as f:
            characters_data = json.load(f)

        characters_data = characters_data.get(language, [])
        
        # Charger les données des personnages depuis le fichier JSON
        with open('data/SJW.json', 'r', encoding='utf-8') as f:
            characters_data = json.load(f)

        # Trouver l'ombre correspondant au nom donné
        shadow = None
        character_folder = None
        for character in characters_data:
            for s in character.get('shadows', []):
                if s['name'] == shadowName:
                    shadow = s
                    character_folder = character['folder']
                    # Mettre à jour les chemins des images
                    if 'image' in shadow:
                        shadow['image'] = f'images/{character_folder}/Shadows/{shadow["image"]}'
                    if 'description' in shadow:
                        shadow['description'] = update_image_paths(shadow['description'], f'images/{character_folder}')
                    
                    # Mettre à jour les compétences (skills) de l'ombre
                    for skill in shadow.get('skills', []):
                        if 'image' in skill:
                            skill['image'] = f'images/{character_folder}/Shadows/Skills/{skill["image"]}'
                        if 'description' in skill:
                            skill['description'] = update_image_paths(skill['description'], f'images/{character_folder}/Shadows/Skills')

                    # Mettre à jour les évolutions de l'ombre
                    for evolution in shadow.get('evolutions', []):
                        if 'description' in evolution:
                            evolution['description'] = update_image_paths(evolution['description'], f'images/{character_folder}/Shadows/Evolutions')

                    # Mettre à jour l'arme associée à l'ombre
                    if 'weapon' in shadow:
                        weapon = shadow['weapon']
                        if 'image' in weapon:
                            weapon['image'] = f'images/{character_folder}/Shadows/Weapons/{weapon["image"]}'
                        if 'codex' in weapon:
                            weapon['codex'] = f'images/{character_folder}/Shadows/Weapons/{weapon["codex"]}'
                        if 'stats' in weapon:
                            weapon['stats'] = update_image_paths(weapon['stats'], f'images/{character_folder}/Shadows/Weapons')
                        for evolution in weapon.get('evolutions', []):
                            if 'description' in evolution:
                                evolution['description'] = update_image_paths(evolution['description'], f'images/{character_folder}/Shadows/Weapons/Evolutions')

                    break

        if not shadow:
            return "Shadow not found", 404

        # Renvoyer le template avec les données de l'ombre
        return render_template('shadow_details.html', shadow=shadow)

    @app.route('/SJW/weapon/<weaponName>')
    def weapon_details(weaponName):
        # Récupérer la langue sélectionnée ou définir 'EN-en' par défaut
        language = session.get('language', 'EN-en')

        # Charger les données des personnages depuis le fichier JSON
        with open('data/SJW.json', 'r', encoding='utf-8') as f:
            characters_data = json.load(f)

        characters_data = characters_data.get(language, [])
        
        with open('data/SJW.json', 'r', encoding='utf-8') as f:
            characters_data = json.load(f)

        # Trouver l'arme correspondant au nom donné
        weapon = None
        character_folder = None
        for character in characters_data:
            for w in character.get('weapon', []):
                if w['name'] == weaponName:
                    weapon = w
                    character_folder = character['folder']
                    # Mettre à jour les chemins des images
                    if 'image' in weapon:
                        weapon['image'] = f'images/{character_folder}/Armes/{weapon["folder"]}/{weapon["image"]}'
                    if 'codex' in weapon:
                        weapon['codex'] = f'images/{character_folder}/Armes/{weapon["folder"]}/{weapon["codex"]}'
                    if 'stats' in weapon:
                        weapon['stats'] = update_image_paths(weapon['stats'], f'images/{character_folder}')
                    for evolution in weapon.get('evolutions', []):
                        if 'description' in evolution:
                            evolution['description'] = update_image_paths(evolution['description'], f'images/{character_folder}')
                    break

        if not weapon:
            return "Weapon not found", 404

        # Renvoyer le template avec les données de l'arme
        return render_template('weapon_details.html', weapon=weapon)