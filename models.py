from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

db = SQLAlchemy()

# Define your database models here

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'employer' or 'intern'

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Define the relationship between Job and InternshipApplication
    internship_applications = db.relationship('InternshipApplication', backref='job', lazy=True)

class InternshipApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intern_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    essay = db.Column(db.Text, nullable=False)
    resume = db.Column(LargeBinary)
    # Add any other fields related to the internship application here

    # Define the relationship between InternshipApplication and User (intern)
    intern = db.relationship('User', backref='internship_applications')