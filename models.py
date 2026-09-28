# Sportsdin - Database Models
# SQLAlchemy models for athlete platform

from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    """User table for login and authentication."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='athlete')  # 'athlete', 'coach', or 'admin'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationship: one user can have one athlete profile (deleted together)
    athlete_profile = db.relationship('Athlete', backref='user', uselist=False, cascade='all, delete-orphan')


class Athlete(db.Model):
    """Athlete profile table - LinkedIn style sports profile."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    sport = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)  # filename of uploaded photo
    is_verified = db.Column(db.Boolean, default=False)  # set true by admin
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships to other tables
    # cascade makes sure achievements/certs/videos are deleted along with profile
    achievements = db.relationship('Achievement', backref='athlete', lazy=True, cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='athlete', lazy=True, cascade='all, delete-orphan')
    videos = db.relationship('Video', backref='athlete', lazy=True, cascade='all, delete-orphan')


class Achievement(db.Model):
    """Achievements table - sports achievements of athletes."""
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=True)  # e.g., "2024" or "June 2024"
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Certificate(db.Model):
    """Certificates table - uploaded certificates."""
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)  # path to uploaded file
    issued_date = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Video(db.Model):
    """Videos table - match videos and YouTube links."""
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    youtube_id = db.Column(db.String(50), nullable=True)  # YouTube video ID
    title = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
