import os
from PIL import Image
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    """Vérifie l'extension du fichier."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image_size_allowed(file_stream, max_size_mb=5):
    """Vérifie que la taille du fichier ne dépasse pas max_size_mb."""
    file_stream.seek(0, os.SEEK_END)
    size = file_stream.tell()
    file_stream.seek(0)
    return size <= max_size_mb * 1024 * 1024

def verify_image(file_stream):
    """
    Vérifie que le fichier est une image valide avec PIL.
    Lève une exception si ce n'est pas le cas.
    """
    img = Image.open(file_stream)
    img.verify()
    file_stream.seek(0)
    return True

def save_image(file_stream, target_folder, target_name):
    """
    Sauvegarde l'image dans le dossier cible après vérification.
    Le nom est sécurisé.
    """
    os.makedirs(target_folder, exist_ok=True)
    filename = secure_filename(target_name)
    save_path = os.path.join(target_folder, filename)
    img = Image.open(file_stream)
    img.save(save_path)
    return save_path

def rename_image(src_path, dest_folder, dest_name):
    """
    Renomme (ou déplace) une image existante vers dest_folder/dest_name.
    Le nom est sécurisé.
    Retourne le nouveau chemin.
    """
    os.makedirs(dest_folder, exist_ok=True)
    dest_filename = secure_filename(dest_name)
    dest_path = os.path.join(dest_folder, dest_filename)
    os.rename(src_path, dest_path)
    return dest_path

def get_image_format(file_stream):
    """
    Retourne le format de l'image (ex: 'PNG', 'WEBP', etc.)
    """
    img = Image.open(file_stream)
    fmt = img.format
    file_stream.seek(0)
    return fmt