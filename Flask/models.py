from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'user' or 'admin'
    grid_square_id = db.Column(db.Integer, db.ForeignKey('grid_squares.id'), nullable=True)
    
    grid_square = db.relationship('GridSquare', backref=db.backref('assigned_user', uselist=False))

class GridSquare(db.Model):
    __tablename__ = 'grid_squares'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)  # e.g., 'U-001'
    status = db.Column(db.Integer, nullable=False, default=0)  # 0=red, 1=yellow, 2=green
    user_id = db.Column(db.Integer, nullable=True)  # This won't be a foreign key to allow deletion without cascade issues