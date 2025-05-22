
import click
from flask.cli import with_appcontext
from datetime import datetime, timedelta, timezone
from scripts.backup_script import run_backup
from scripts.cleanup_backups import run_cleanup


@click.command('seed-stale-user')
@with_appcontext
def seed_stale_user():
    """Opretter en test-bruger med pw_changed_at > 7 dage."""
    # Importér først når kommandoen kører
    from webapp import db
    from webapp.models import User, UserRole

    stale = User(
        username='staleuser',
        email='stale@example.dk',
        password_hash='dummyhash',
        role=UserRole.watcher,
        pw_changed_at=datetime.now(timezone.utc) - timedelta(days=8),
        pw_expires_at=datetime.now(timezone.utc) - timedelta(days=1)
    )
    db.session.add(stale)
    db.session.commit()
    click.echo("✅ Oprettet staleuser")

@click.command('clean-users')
@with_appcontext
def clean_users_command():
    """Slet alle brugere, som ikke har skiftet kodeord inden for 7 dage."""
    # Importér først når kommandoen kører
    from webapp.jobs.cleanup import delete_stale_users

    delete_stale_users()
    click.echo("✅ delete_stale_users kørt")


@click.command("seed-admin")
@with_appcontext
def seed_admin():
    """Opret admin-bruger med telefonnummer hvis den ikke findes."""
    from werkzeug.security import generate_password_hash
    from webapp import db
    from webapp.models import User, UserRole

    existing = User.query.filter_by(username="admin").first()
    if existing:
        click.echo("⚠️ Admin-bruger findes allerede – hopper over.")
        return

    admin = User(
        username="admin",
        email="admin@example.com",
        phone_number="+4560701547",  
        password_hash=generate_password_hash("hemmeligtpw"),
        role=UserRole.admin
    )
    db.session.add(admin)
    db.session.commit()
    click.echo("✅ Admin-bruger oprettet: admin / hemmeligtpw")

   
@click.command("backup")
@with_appcontext
def backup_command():
    """Kør backup-scriptet."""
    run_backup()

@click.command("cleanup")
@with_appcontext
def cleanup_command():
    """Sletter gamle backup-filer, hvis der er flere end 10."""
    run_cleanup()