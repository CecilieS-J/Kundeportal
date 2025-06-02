import os
import logging
from datetime import datetime, timedelta, timezone
from ..models import User
from ..mail import send_alert

# Ensure the 'logs' directory exists
os.makedirs('logs', exist_ok=True)

# Logger setup for the notification job
notif_logger = logging.getLogger('notifications')
notif_handler = logging.FileHandler('logs/notifications.log')
notif_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
notif_logger.addHandler(notif_handler)
notif_logger.setLevel(logging.INFO)

def remind_expiring_passwords():
    """
    Sends a reminder email on day 5 after account creation to users who have not set their password.
    Informs them that their account will be deleted if they don't set a password within 7 days.
    """
    now = datetime.now(timezone.utc)
    # Define a window for accounts created ~5 days ago (between 4.5 and 5.5 days to account for timing)
    remind_threshold_start = now - timedelta(days=5.5)
    remind_threshold_end = now - timedelta(days=4.5)

    users = User.query.filter(
        User.pw_changed_at.is_(None),  # No password set
        User.created_at <= remind_threshold_start,
        User.created_at >= remind_threshold_end
    ).all()

    for u in users:
        subject = "Reminder: Set Your Password or Account Will Be Deleted"
        body = (
            f"Dear {u.username},\n\n"
            f"Your account was created on {u.created_at.strftime('%d/%m/%Y %H:%M')} UTC, "
            "but you have not yet set your password using the link sent to you.\n"
            "Please set your password within the next 2 days, or your account will be deleted on day 7.\n\n"
            "Best regards, IT Support"
        )
        try:
            send_alert(subject, [u.email], body)
            notif_logger.info(
                f"Reminder sent to {u.username} <{u.email}>; created_at={u.created_at}"
            )
        except Exception as e:
            notif_logger.error(f"Could not send reminder to {u.username}: {e}")