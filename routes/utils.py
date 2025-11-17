from flask import session
import unicodedata
import re
from flask import url_for
import os
import os
import zipfile
import shutil

def is_admin():
    rights = session.get('rights', [])
    return 'Admin' in rights or 'SuperAdmin' in rights

def normalize_focus_stats(val):
    if isinstance(val, list):
        if len(val) == 1 and isinstance(val[0], str) and ',' in val[0]:
            return sorted([v.strip() for v in val[0].split(',') if v.strip()])
        return sorted([v.strip() for v in val if v])
    if isinstance(val, str):
        return sorted([v.strip() for v in val.split(',') if v.strip()])
    return []

def normalize_stats(val):
    if isinstance(val, list):
        return ','.join([v.strip() for v in val if v])
    if isinstance(val, str):
        return ','.join([v.strip() for v in val.split(',') if v.strip()])
    return ''

def normalize_text(val):
    if val is None:
        return ''
    return val.replace('\r\n', '\n').replace('\r', '\n').strip()

def render_tags(description, tags_list, base_path):
    def normalize_tag(tag):
        tag = tag.replace("’", "'").replace("`", "'").replace("´", "'")
        return ''.join(
            c for c in unicodedata.normalize('NFD', tag)
            if unicodedata.category(c) != 'Mn'
        ).lower().strip()

    def find_tag(tag):
        tag_norm = normalize_tag(tag)
        for item in tags_list:
            tag_value = item.get('tag')
            if tag_value and normalize_tag(tag_value) == tag_norm:
                return item
        return None

    def replacer(match):
        tag_raw = match.group(1)
        parts = tag_raw.split('|')
        tag = parts[0].strip()
        only_img = len(parts) > 1 and parts[1].strip().lower() == 'img'
        tag_info = find_tag(tag)
        if tag_info and tag_info.get('image'):
            img_path = tag_info['image']
            if not img_path.startswith('images/'):
                img_url = url_for('static', filename=f"{base_path}/{img_path}")
            else:
                img_url = url_for('static', filename=img_path)
            img_html = f"<img src='{img_url}' alt='{tag_info.get('tag', tag)}' class='tag-img'>"
            if only_img:
                return img_html
            else:
                return f"{img_html} [{tag_info.get('tag', tag)}]"
        return match.group(0)

    result = re.sub(r"\[([^\]]+)\]", replacer, description).replace("\n", "<br>")
    return result

def update_image_paths(description, base_path):
    if not description:
        return description
    updated_description = description
    if f"src='{url_for('static', filename=base_path)}/" not in description:
        updated_description = description.replace(
            "src='",
            f"src='{url_for('static', filename=base_path)}/"
        )
    return updated_description.replace("\n", "<br>")

def process_description(description, tags_list, base_path):
    if not description:
        return description
    if re.search(r"<img\s+src=.*?>\s*\[[^\]]+\]", description):
        return update_image_paths(description, base_path)
    elif re.search(r"\[[^\]]+\]", description):
        return render_tags(description, tags_list, base_path)
    else:
        return description.replace("\n", "<br>")

def none_to_empty(val):
    return "None" if val == "" else val

def focus_stats_equal(a, b):
    return set(normalize_focus_stats(a)) == set(normalize_focus_stats(b))

def extract_zip(zip_file, target_folder, expected_folder_name, file_prefix_check=None):
    temp_extract = os.path.join("tmp", "extract_zip")
    if os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(zip_file) as zf:
        zf.extractall(temp_extract)

    subfolders = [f for f in os.listdir(temp_extract) if os.path.isdir(os.path.join(temp_extract, f))]
    if subfolders:
        src_folder = os.path.join(temp_extract, subfolders[0])
        if subfolders[0] != expected_folder_name:
            os.rename(src_folder, os.path.join(temp_extract, expected_folder_name))
            src_folder = os.path.join(temp_extract, expected_folder_name)
        shutil.move(src_folder, target_folder)
    else:
        os.makedirs(target_folder, exist_ok=True)
        for fname in os.listdir(temp_extract):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                if file_prefix_check and not fname.startswith(file_prefix_check):
                    shutil.rmtree(temp_extract)
                    raise ValueError(f"Image '{fname}' must start with '{file_prefix_check}'")
                shutil.move(os.path.join(temp_extract, fname), os.path.join(target_folder, fname))

    shutil.rmtree(temp_extract)

def asset_url_for(endpoint, filename):
    """Génère une URL pour un fichier statique avec un timestamp pour le cache-busting."""
    static_folder = 'static'  # Assurez-vous que cela correspond à votre dossier statique
    file_path = os.path.join(static_folder, filename)
    if os.path.exists(file_path):
        timestamp = int(os.path.getmtime(file_path))
        return url_for(endpoint, filename=filename, v=timestamp)
    return url_for(endpoint, filename=filename)