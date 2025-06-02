import os
import logging
from datetime import datetime, timedelta, timezone
from .. import db
from ..models import User
from ..mail import send_alert

# Ensure the 'logs' directory exists
os.makedirs('logs', exist_ok=True)




# Logger setup for the cleanup job
cleanup_logger = logging.getLogger('cleanup')
cleanup_handler = logging.FileHandler('logs/cleanup.log')
cleanup_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
cleanup_logger.addHandler(cleanup_handler)
cleanup_logger.setLevel(logging.INFO)

def delete_stale_users():
    """
    Deletes users who have not set their password within 7 days of account creation.
    Logs each deletion and sends an alert if an error occurs.
    """
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        stale = User.query.filter(
            User.pw_changed_at.is_(None),  # Tjekker for NULL (aldrig sat adgangskode)
            User.created_at < cutoff       # Tjekker, om kontoen er ældre end 7 dage
        ).all()
        count = len(stale)
        for u in stale:
            cleanup_logger.info(f"Deleting user id={u.id}, username={u.username}, created_at={u.created_at}")
            db.session.delete(u)
        db.session.commit()
        cleanup_logger.info(f"Deleted {count} stale users")
    except Exception as e:
        db.session.rollback()
        cleanup_logger.exception("Error deleting stale users")
        send_alert(
            "Cleanup-fejl i Kundeportal",
            ["admin@magasin.dk"],
            f"Fejl i cleanup-jobbet:\n\n{e}"
        )
        raise