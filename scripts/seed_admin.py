# scripts/seed_admin.py

from werkzeug.security import generate_password_hash
from webapp import app, db
from webapp.models import User, UserRole

def seed_admin():
    """Opret admin-bruger, hvis den ikke allerede findes."""
    username = "admin"
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"Bruger '{username}' findes allerede — hopper over.")
        return

    pw_hash = generate_password_hash("hemmeligtpw")
    admin = User(
        username=username,
        email="admin@example.com",   # Du kan ændre til en gyldig mail
        password_hash=pw_hash,
        role=UserRole.admin
    )
    db.session.add(admin)
    db.session.commit()
    print(f"Admin-bruger oprettet: {username} / hemmeligtpw")

if __name__ == "__main__":
    # Sørg for at køre seed_admin() under Flask's app context:
    with app.app_context():
        seed_admin()
