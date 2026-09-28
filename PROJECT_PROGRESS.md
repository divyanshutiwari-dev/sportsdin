# PROJECT PROGRESS TRACKER

## Overall Status
- Project: Sportsdin - LinkedIn for Athletes
- Type: College Mini Project
- Framework: Flask + SQLite + Bootstrap 5
- Current Phase: UI/UX Upgrade Complete - Core Features Working

---

## What Works Right Now (Tested)

1. Home page with hero section, features, stats band
2. About page with mission + how-it-works steps
3. Register (athlete or coach) -> auto login -> dashboard
4. Login / Logout with Flask-Login sessions
5. Dashboard with profile header card + quick action cards
6. Profile page: cover, avatar, bio/sport/location edit, photo upload
7. Achievements: add + delete (with owner check)
8. Certificates: upload PDF/PNG/JPG, view from profile
9. Match videos: paste any YouTube link, auto-extracts video ID, embedded player on profile
10. Search athletes by name / sport / location filters

---

## Files In The Project

Backend:
- app.py          - builds the Flask app, DB, Flask-Login (no routes here)
- run.py          - THE FILE YOU RUN - starts the website
- config.py       - secret key, SQLite path, upload folder
- models.py       - User, Athlete, Achievement, Certificate, Video tables
- routes.py       - all route handlers (including home/about)
- requirements.txt - dependencies list

Frontend:
- static/css/style.css      - full sports theme (blue/white/black/grey)
- templates/base.html       - navbar + footer + flash messages
- templates/home.html       - landing page
- templates/about.html      - about page
- templates/register.html   - split-screen signup
- templates/login.html      - split-screen signin
- templates/dashboard.html  - user home after login
- templates/profile.html    - full profile view + inline edit form
- templates/add_achievement.html
- templates/upload_certificate.html
- templates/add_video.html
- templates/search.html     - athlete discovery page

Other:
- sportsdin.db              - SQLite database (auto-created)
- static/uploads/           - uploaded photos and certificates
- PROJECT_CONTENT.md.txt    - original project constitution
- PROJECT_PROGRESS.md       - this file

---

## How To Run

1. Open the project folder in VS Code
2. Install once: `pip install flask flask-sqlalchemy flask-login`
3. Run: `python run.py`   (NOT app.py)
4. Open browser at http://127.0.0.1:5000

Important: always start with run.py. Running app.py directly causes a
double-import bug where most pages show 404/500 errors.

---

## Bugs Fixed During Build

- Circular import between app.py and routes.py -> routes imported after app creation
- login_required was imported from wrong place -> now from flask_login
- config loader typo (from_config -> from_object)
- login_manager.init_app was called on itself -> now called on app
- Deleting a user crashed because related rows had no cascade -> added cascade='all, delete-orphan'
- YouTube link handling -> accepts full URL or plain ID automatically
- DOUBLE-IMPORT BUG (the big one): running `python app.py` loaded the file twice
  (as __main__ and as module 'app'), so routes registered on the wrong app object
  and every page except home/about gave 404/500. Fix: app.py only builds the app,
  all routes live in routes.py, and run.py starts the server.

---

## Remaining Phases

### Phase 8: Search & Filter Athletes - DONE (search page live)
### Phase 9 (Optional): Admin Panel - Not started
- Admin verify athletes
- Delete users safely (cascade is already in place)
- Public athlete profile view (/athlete/<id> for coaches)

---

## Development Notes
- Beginner-friendly code style maintained
- No enterprise patterns, no over-engineering
- Poppins font, Bootstrap Icons, custom CSS only (no Tailwind)
- Colors: blue #0a66c2, dark navy #0b1f3a, grey #6b7280, light #f4f6f8
