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
        character_info = next((char for char in characters_data if char['alias'] == alias), None)

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
                passive['image'] = f'images/{character_folder}/{passive["image"]}'
            if 'description' in passive:
                passive['description'] = update_image_paths(passive['description'], f'images/{character_folder}')

        # Mettre à jour les descriptions des skills
        for skill in character_info.get('skills', []):
            if 'image' in skill:
                skill['image'] = f'images//{character_folder}/{skill["image"]}'
            if 'description' in skill:
                skill['description'] = update_image_paths(skill['description'], f'images/{character_folder}')

        # Mettre à jour les descriptions des armes
        for weapon in character_info.get('weapon', []):
            if 'image' in weapon:
                weapon['image'] = f'images/{character_folder}/{weapon["image"]}'
            if 'stats' in weapon:
                weapon['stats'] = update_image_paths(weapon['stats'], f'images//{character_folder}')
            # Mettre à jour les évolutions des armes
            for evolution in weapon.get('evolutions', []):
                if 'description' in evolution:
                    evolution['description'] = update_image_paths(evolution['description'], f'images//{character_folder}')

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
                artefact['image'] = f'images/Artefacts/{artefact["image"]}'

            # Mettre à jour les images des noyaux
            for core in equipment_set.get('cores', []):
                core['image'] = f'images/Noyaux/{core["image"]}'

        # Renvoyer le template avec les données du personnage
        return render_template('SJW.html', character=character_info)