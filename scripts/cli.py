
import click
from flask.cli import with_appcontext
from datetime import datetime, timedelta, timezone

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