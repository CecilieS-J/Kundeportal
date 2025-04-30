# scripts/seed_admin.py

from werkzeug.security import generate_password_hash
from webapp import app, db
from webapp.models import User, UserRole

with app.app_context():
    username = "dataansvarlig"
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"Bruger '{username}' findes allerede—hopper over oprettelse.")
    else:
        pw_hash = generate_password_hash("hemmeligtpw")
        admin = User(
            username=username,
            password_hash=pw_hash,
            role=UserRole.dataansvarlig
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin-bruger oprettet: {username} / hemmeligtpw")
