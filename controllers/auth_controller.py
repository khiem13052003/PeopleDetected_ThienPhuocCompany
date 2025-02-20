class AuthController:
    def __init__(self, db):
        self.db = db

    def login(self, username, password):
        user = self.db.get_user(username)
        return user and user["password"] == password
