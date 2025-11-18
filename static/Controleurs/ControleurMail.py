from flask import render_template
from flask_mail import Mail, Message

mail = Mail()

def init_mail(app, config):
    """
    Initialise l'extension Flask-Mail avec la configuration de l'application.
    """
    app.config['MAIL_SERVER'] = config.get_config('SMTP', 'MAIL_SERVER')
    app.config['MAIL_PORT'] = int(config.get_config('SMTP', 'MAIL_PORT'))
    app.config['MAIL_USE_TLS'] = config.get_config('SMTP', 'MAIL_USE_TLS').lower() in ['true', '1', 't']
    app.config['MAIL_USERNAME'] = config.get_config('SMTP', 'MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = config.get_config('SMTP', 'MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = config.get_config('SMTP', 'MAIL_DEFAULT_SENDER')
    mail.init_app(app)

def send_password_reset_email(recipient_email, reset_url):
    """
    Construit et envoie l'e-mail de réinitialisation du mot de passe.

    :param recipient_email: L'adresse e-mail du destinataire.
    :param reset_url: L'URL complète pour la réinitialisation du mot de passe.
    """
    msg = Message("Réinitialisation de votre mot de passe",
                  recipients=[recipient_email])

    msg.html = render_template('emails/reset_password_email.html',
                               reset_url=reset_url)

    mail.send(msg)
