import logging
import os
from flask import session
from .ControleurConf import ControleurConf

# Logger global
logger = logging.getLogger("SoloLevelingLogger")
logger.propagate = False

# Initialisation du handler au chargement du module
conf = ControleurConf()
log_file_path = conf.get_config('LOG', 'file')
log_file_path = os.path.abspath(log_file_path)
log_level = conf.get_config('LOG', 'level').upper()
log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

if not logger.handlers:
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(log_levels.get(log_level, logging.INFO))
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
logger.setLevel(log_levels.get(log_level, logging.INFO))

def write_log(message, log_level=None, username=None):
    # Niveau de log dynamique
    if log_level is None:
        level = log_levels.get(log_level, logging.INFO)
    else:
        level = log_levels.get(log_level.upper(), logging.INFO)

    if username:
        message = f"{username} - {message}"

    try:
        logger.log(level, message)
    except Exception as e:
        print(f"Failed to write log: {e}")
