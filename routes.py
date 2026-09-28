# Sportsdin - Route Handlers
# URL routes and request processing

import os
import mimetypes

from flask import (render_template, redirect, url_for,
                   flash, request, current_app, send_file)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import app, db
from models import User, Athlete, Achievement, Certificate, Video


# ---------- Home / About ----------

@app.route('/')
def home():
    """Landing page."""
    return render_template('home.html')


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


# ---------- Registration ----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Create a new user account."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role', 'athlete')

        # check if email is already taken
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        hashed = generate_password_hash(password)
        new_user = User(email=email, password=hashed, name=name, role=role)
        db.session.add(new_user)
        db.session.commit()

        # every athlete gets a profile right away (coaches don't need one)
        if new_user.role == 'athlete':
            profile = Athlete(user_id=new_user.id)
            db.session.add(profile)
            db.session.commit()

        flash('Account created! Welcome to Sportsdin.', 'success')
        login_user(new_user)
        return redirect(url_for('dashboard'))

    return render_template('register.html')


# ---------- Login / Logout ----------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log an existing user in."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Log the user out."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ---------- Dashboard ----------

@app.route('/dashboard')
@login_required
def dashboard():
    """Main landing page after login."""
    return render_template('dashboard.html')


# ---------- Profile ----------

def save_uploaded_file(file):
    """Save an uploaded file and return its safe filename."""
    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)
    return filename


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update athlete bio, sport, location and photo."""
    athlete = Athlete.query.filter_by(user_id=current_user.id).first()

    if not athlete:
        athlete = Athlete(user_id=current_user.id)
        db.session.add(athlete)

    athlete.bio = request.form.get('bio')
    athlete.sport = request.form.get('sport')
    athlete.location = request.form.get('location')

    photo = request.files.get('profile_image')
    if photo and photo.filename != '':
        athlete.profile_image = save_uploaded_file(photo)

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/profile')
@login_required
def profile():
    """Show the logged-in athlete's full profile."""
    athlete = Athlete.query.filter_by(user_id=current_user.id).first()

    # auto-create a profile if the user doesn't have one yet (e.g. admin / coach)
    if not athlete:
        athlete = Athlete(user_id=current_user.id)
        db.session.add(athlete)
        db.session.commit()

    return render_template('profile.html', athlete=athlete)


# ---------- Achievements ----------

@app.route('/achievements/add', methods=['GET', 'POST'])
@login_required
def add_achievement():
    """Add a new achievement."""
    athlete = Athlete.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        title = request.form.get('title')

        if title:
            achievement = Achievement(
                athlete_id=athlete.id,
                title=title,
                description=request.form.get('description'),
                date=request.form.get('date')
            )
            db.session.add(achievement)
            db.session.commit()
            flash('Achievement added!', 'success')
            return redirect(url_for('profile'))

        flash('Achievement title is required.', 'danger')

    return render_template('add_achievement.html')


@app.route('/achievements/delete/<int:achievement_id>')
@login_required
def delete_achievement(achievement_id):
    """Delete one of your own achievements."""
    achievement = Achievement.query.get_or_404(achievement_id)
    athlete = Athlete.query.filter_by(user_id=current_user.id).first()

    if achievement.athlete_id != athlete.id:
        flash('You cannot delete that achievement.', 'danger')
        return redirect(url_for('profile'))

    db.session.delete(achievement)
    db.session.commit()
    flash('Achievement deleted.', 'success')
    return redirect(url_for('profile'))


# ---------- Certificates ----------

ALLOWED_CERT_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


def allowed_certificate_file(filename):
    """Check the uploaded certificate has an allowed extension."""
    extension = filename.rsplit('.', 1)[-1].lower()
    return extension in ALLOWED_CERT_EXTENSIONS


@app.route('/certificates/upload', methods=['GET', 'POST'])
@login_required
def upload_certificate():
    """Upload a certificate file."""
    athlete = Athlete.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        title = request.form.get('title')
        file = request.files.get('certificate_file')

        if not title:
            flash('Certificate title is required.', 'danger')
            return render_template('upload_certificate.html')

        if not file or file.filename == '':
            flash('Please choose a file to upload.', 'danger')
            return render_template('upload_certificate.html')

        if not allowed_certificate_file(file.filename):
            flash('Only PDF, PNG or JPG files are allowed.', 'danger')
            return render_template('upload_certificate.html')

        filename = save_uploaded_file(file)
        certificate = Certificate(
            athlete_id=athlete.id,
            title=title,
            file_path='uploads/' + filename,
            issued_date=request.form.get('issued_date')
        )
        db.session.add(certificate)
        db.session.commit()
        flash('Certificate uploaded!', 'success')
        return redirect(url_for('profile'))

    return render_template('upload_certificate.html')


@app.route('/certificates/view/<int:certificate_id>')
@login_required
def view_certificate(certificate_id):
    """View a certificate inline (no download)."""
    certificate = Certificate.query.get_or_404(certificate_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                             certificate.file_path.replace('uploads/', ''))
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    return send_file(file_path, mimetype=mime_type,
                     download_name=certificate.title,
                     as_attachment=False)


# ---------- Match Videos ----------

@app.route('/videos/add', methods=['GET', 'POST'])
@login_required
def add_video():
    """Add a YouTube match video link."""
    athlete = Athlete.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        youtube_link = request.form.get('youtube_link', '')

        # accept both full links and plain video ids
        youtube_id = youtube_link.split('v=')[-1].split('&')[0]

        if youtube_id:
            video = Video(
                athlete_id=athlete.id,
                youtube_id=youtube_id,
                title=request.form.get('title'),
                description=request.form.get('description')
            )
            db.session.add(video)
            db.session.commit()
            flash('Video added to your profile!', 'success')
            return redirect(url_for('profile'))

        flash('Please paste a valid YouTube link.', 'danger')

    return render_template('add_video.html')


# ---------- Search ----------

SPORT_LIST = ['Football', 'Basketball', 'Cricket', 'Tennis',
              'Volleyball', 'Badminton', 'Hockey', 'Athletics', 'Others']


@app.route('/search')
def search():
    """Search athletes by name, sport and/or location."""
    query = request.args.get('query', '').strip()
    sport_filter = request.args.get('sport', '')
    location_filter = request.args.get('location', '')

    results = Athlete.query.join(User)

    if query:
        results = results.filter(User.name.ilike('%' + query + '%'))
    if sport_filter:
        results = results.filter(Athlete.sport.ilike('%' + sport_filter + '%'))
    if location_filter:
        results = results.filter(Athlete.location.ilike('%' + location_filter + '%'))

    return render_template('search.html',
                           athletes=results.all(),
                           query=query,
                           sport_filter=sport_filter,
                           location_filter=location_filter,
                           sport_list=SPORT_LIST)


# ---------- Public Athlete Profile ----------

@app.route('/athlete/<int:athlete_id>')
@login_required
def public_profile(athlete_id):
    """Anyone logged in can view an athlete's profile (read only)."""
    athlete = Athlete.query.get_or_404(athlete_id)
    return render_template('public_profile.html', athlete=athlete)


# ---------- Admin Panel ----------

def admin_only():
    """Returns True if the logged-in user is an admin."""
    return current_user.is_authenticated and current_user.role == 'admin'


@app.route('/admin')
@login_required
def admin_panel():
    """Admin dashboard - manage users."""
    if not admin_only():
        flash('You are not allowed to open that page.', 'danger')
        return redirect(url_for('dashboard'))

    users = User.query.order_by(User.id).all()
    stats = {
        'total': User.query.count(),
        'athletes': User.query.filter_by(role='athlete').count(),
        'coaches': User.query.filter_by(role='coach').count(),
        'verified': Athlete.query.filter_by(is_verified=True).count()
    }
    return render_template('admin.html', users=users, stats=stats)


@app.route('/admin/verify/<int:user_id>')
@login_required
def verify_athlete(user_id):
    """Mark an athlete as verified / unverified (toggles)."""
    if not admin_only():
        flash('Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    user = User.query.get_or_404(user_id)

    if not user.athlete_profile:
        flash('Coaches do not have profiles to verify.', 'warning')
        return redirect(url_for('admin_panel'))

    user.athlete_profile.is_verified = not user.athlete_profile.is_verified
    db.session.commit()

    if user.athlete_profile.is_verified:
        flash(user.name + ' is now verified.', 'success')
    else:
        flash('Verification removed for ' + user.name + '.', 'info')
    return redirect(url_for('admin_panel'))


@app.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    """Remove a user and all their data from Sportsdin."""
    if not admin_only():
        flash('Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    # safety: an admin should not be able to delete their own account
    if user_id == current_user.id:
        flash('You cannot delete your own admin account.', 'danger')
        return redirect(url_for('admin_panel'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(user.name + ' has been removed.', 'success')
    return redirect(url_for('admin_panel'))
