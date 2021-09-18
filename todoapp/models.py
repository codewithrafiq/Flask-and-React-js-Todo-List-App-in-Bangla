from datetime import datetime
from todoapp import db

class Uses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(500), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(500))
    todos = db.relationship('Todo', backref='user', lazy='dynamic')
    def __repr__(self):
        return self.email

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    data = db.Column(db.DateTime,default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('uses.id'), nullable=False)