from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    books = db.relationship('UserBook', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_books_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    authors = db.Column(db.String(200))
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    users = db.relationship('UserBook', backref='book', lazy=True)

class UserBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'want_to_read', 'reading', 'read'
    rating = db.Column(db.Integer)  # 1-5 stars
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_status_changed = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
