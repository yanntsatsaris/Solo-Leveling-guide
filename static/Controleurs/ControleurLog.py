import logging
import inspect
import os
from flask import session
from .ControleurConf import ControleurConf

# Récupérer le chemin du fichier de log via ControleurConf
conf = ControleurConf()
log_file_path = conf.get_config('LOG', 'file')
if not log_file_path:
    log_file_path = "/var/log/Solo-Leveling-guide/Solo-Leveling-guide.log"
log_file_path = os.path.abspath(log_file_path)
log_dir = os.path.dirname(log_file_path)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def write_log(message, log_level=None, username=None):
    # Utilisation du niveau de log par défaut si non fourni
    if log_level is None:
        log_level = "INFO"
    else:
        log_level = log_level.upper()

    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    caller_function = inspect.stack()[1].function

    if username:
        message = f"{username} - {message}"

    try:
        if log_level not in log_levels:
            raise ValueError(f"Invalid log level: {log_level}")

        # Logger global pour tout le projet
        logger = logging.getLogger("SoloLevelingLogger")
        logger.setLevel(log_levels[log_level])

        # Ajoute le handler une seule fois
        if not logger.handlers:
            fh = logging.FileHandler(log_file_path)
            fh.setLevel(log_levels[log_level])
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        logger.log(log_levels[log_level], message)

    except Exception as e:
        print(f"Failed to write log: {e}")
        with open(os.path.join(log_dir, "error.log"), "a") as error_log:
            error_log.write(f"Failed to write log: {e}\n")
