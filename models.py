from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define your database models here

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Add employer-related fields here

class Intern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
