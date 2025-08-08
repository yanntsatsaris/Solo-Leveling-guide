from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, user_loader
from flask import current_app, session

class User(UserMixin):
    def __init__(self, username, rights):
        self.id = username
        self.rights = rights

    def get_id(self):
        return self.id

def user_loader(user_id):
    rights = session.get('rights', [])
    return User(user_id, rights)