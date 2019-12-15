from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.Date, index=True)
    posting_date = db.Column(db.Date, index=False)
    description = db.Column(db.String(length=100), index=False)
    debits = db.Column(db.Float, index=False)
    credits = db.Column(db.Float, index=False)
    balance = db.Column(db.Float, index=False)
    category = db.Column(db.String(length=100), index=True)
    account_holder = db.Column(db.String(length=20), index=False)

class CategoryRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(length=50), index=True)
    string_match = db.Column(db.String(length=100), index=False)
    date_match = db.Column(db.Date, index=False)
    exact_rule = db.Column(db.Boolean, index=False)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
