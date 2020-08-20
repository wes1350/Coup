import sys
sys.path.insert(0,'..')  # For importing app config, required for using db
from coup import app, db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

DEFAULT_ELO = 1000

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    elo = db.Column(db.Integer, server_default=str(DEFAULT_ELO), nullable=False)
    n_games = db.Column(db.Integer, server_default="0", nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_elo(self, elo):
        self.elo = elo

    def get_elo(self):
        return self.elo

    def add_games(self, n):
        self.n_games += n

class AgentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    elo = db.Column(db.Integer, server_default=str(DEFAULT_ELO), nullable=False)
    n_games = db.Column(db.Integer, server_default="0", nullable=False)

    def __repr__(self):
        return "<Agent {}>".format(self.name)

    def set_elo(self, elo):
        self.elo = elo

    def get_elo(self):
        return self.elo

    def add_games(self, n):
        self.n_games += n

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
