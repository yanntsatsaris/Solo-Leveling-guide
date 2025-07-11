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
    print(f"write_log called with message: {message}, level: {log_level}")
    # Get the configuration
    
    # Use the provided log_level or fall back to the default from the configuration
    if log_level is None:
        log_level = "INFO"
    else:
        log_level = log_level.upper()

    # Map string log levels to logging module constants
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    # Get the name of the calling function
    caller_function = inspect.stack()[1].function

    # Add username to the log message if available
    if username:
        message = f"{username} - {message}"

    # Perform the log writing logic here
    try:
        # Ensure the log level is valid
        if log_level not in log_levels:
            raise ValueError(f"Invalid log level: {log_level}")

        # Create a logger
        logger = logging.getLogger(caller_function)
        logger.setLevel(log_levels[log_level])

        # Check if the logger already has handlers
        if not logger.handlers:
            # Créez un FileHandler
            fh = logging.FileHandler(log_file_path)
            fh.setLevel(log_levels[log_level])

            # Définir le format des logs
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)

            # Ajoutez le handler au logger
            logger.addHandler(fh)

        # Log the message with the caller function
        logger.log(log_levels[log_level], message)

    except Exception as e:
        print(f"Failed to write log: {e}")
        # Optionnel : écrire l'erreur dans un fichier séparé
        with open("/var/log/Solo-Leveling-guide/error.log", "a") as error_log:
            error_log.write(f"Failed to write log: {e}\n")
