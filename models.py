from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Conversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100), nullable=False)
    original_format = db.Column(db.String(10), nullable=False)
    new_format = db.Column(db.String(10), nullable=False)
    new_filename = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
