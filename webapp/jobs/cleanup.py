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
    Deletes users who have not changed their password within 7 days
    (considered inactive or stale accounts).
    Logs each deletion and sends an alert if an error occurs.
    """
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        stale = User.query.filter(User.pw_changed_at < cutoff).all()
        count = len(stale)
        for u in stale:
            cleanup_logger.info(f"Deleting user id={u.id}, username={u.username}")
            db.session.delete(u)
        db.session.commit()
        cleanup_logger.info(f"Deleted {count} stale users")
    except Exception as e:
        db.session.rollback()
        cleanup_logger.exception("Error deleting stale users")
        send_alert(
            "Cleanup‐fejl i Kundeportal",
            ["admin@magasin.dk"],
            f"Fejl i cleanup‐jobbet:\n\n{e}"
        )
        raise
