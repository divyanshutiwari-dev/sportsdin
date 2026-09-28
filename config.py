import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Secret key for session management
    SECRET_KEY = 'sportsdin-college-project-2026'

    # Database configuration - SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'sportsdin.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folder for profile photos, certificates, videos
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')

    # Ensure upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Number of athletes per page for pagination
    ATHLETES_PER_PAGE = 10