import logging
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
    import inspect
    caller_function = inspect.stack()[1].function

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

    if username:
        message = f"{username} - {message}"

    # Ajoute le nom de la fonction appelante au message
    message = f"[{caller_function}] {message}"

    try:
        logger = logging.getLogger("SoloLevelingGuide")
        logger.setLevel(logging.DEBUG)
        if not logger.handlers:
            fh = logging.FileHandler(log_file_path)
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        logger.log(log_levels[log_level], message)
    except Exception as e:
        print(f"Failed to write log: {e}")
        with open("/var/log/Solo-Leveling-guide/error.log", "a") as error_log:
            error_log.write(f"Failed to write log: {e}\n")
