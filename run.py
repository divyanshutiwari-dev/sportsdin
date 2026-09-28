# Sportsdin - Website Starter
# Run the website with:  python run.py

from app import app, db

# all routes live in routes.py, importing them registers them on the app
import routes  # noqa: F401


# create database tables before starting
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
