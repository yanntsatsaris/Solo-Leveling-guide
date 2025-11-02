from flask_mail import Mail, Message
from flask import render_template
from .ControleurConf import ControleurConf

mail = Mail()

def configure_mail(app):
    conf = ControleurConf()
    app.config['MAIL_SERVER'] = conf.get_config('SMTP', 'server')
    app.config['MAIL_PORT'] = int(conf.get_config('SMTP', 'port'))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = conf.get_config('SMTP', 'username')
    app.config['MAIL_PASSWORD'] = conf.get_config('SMTP', 'password')
    app.config['MAIL_DEFAULT_SENDER'] = conf.get_config('SMTP', 'sender')
    mail.init_app(app)

def send_email(to, subject, template, **kwargs):
    """
    Fonction générique pour envoyer un e-mail en utilisant un template HTML.
    """
    msg = Message(subject, recipients=[to])
    msg.html = render_template(template, **kwargs)
    mail.send(msg)
