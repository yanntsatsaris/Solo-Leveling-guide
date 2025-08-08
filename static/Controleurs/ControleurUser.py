from flask_login import UserMixin
from flask import session

class User(UserMixin):
    def __init__(self, username, rights):
        self.id = username
        self.rights = rights

    def get_id(self):
        return self.id

def user_loader(user_id):
    rights = session.get('rights', [])
    return User(user_id, rights)