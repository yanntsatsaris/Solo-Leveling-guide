import logging
import os
from flask import session
from .ControleurConf import ControleurConf

# Logger global
logger = logging.getLogger("SoloLevelingLogger")
logger.propagate = False

def write_log(message, log_level=None, username=None):
    conf = ControleurConf()
    log_file_path = conf.get_config('LOG', 'file')
    log_file_path = os.path.abspath(log_file_path)  # Chemin absolu

    # Niveau de log
    if log_level is None:
        log_level = conf.get_config('LOG', 'level').upper()
    else:
        log_level = log_level.upper()

    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    # Ajoute le handler une seule fois
    if not logger.handlers:
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(log_levels.get(log_level, logging.INFO))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    logger.setLevel(log_levels.get(log_level, logging.INFO))

    # Ajoute le username si présent
    if username:
        message = f"{username} - {message}"

    try:
        logger.log(log_levels.get(log_level, logging.INFO), message)
    except Exception as e:
        print(f"Failed to write log: {e}")
