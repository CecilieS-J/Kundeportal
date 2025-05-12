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
    Sends a reminder email to users who have not changed their password
    since their account was created by the data administrator.
    """
    now = datetime.now(timezone.utc)
    # Users who have a set password change timestamp from creation, but haven't changed it yet
    remind_threshold = now - timedelta(hours=48)  # optional threshold to avoid spamming new users

    users = User.query.filter(
        User.pw_changed_at <= remind_threshold
    ).all()

    for u in users:
        subject = "Reminder: Please change your password"
        body = (
            f"Dear {u.username},\n\n"
            f"Your account was created on {u.pw_changed_at.strftime('%d/%m/%Y %H:%M')} UTC, "
            "but you have not changed your password since then.\n"
            "For security reasons, please change your password as soon as possible.\n\n"
            "Best regards, IT Support"
        )
        try:
            send_alert(subject, [u.email], body)
            notif_logger.info(
                f"Reminder sent to {u.username} <{u.email}>; pw_changed_at={u.pw_changed_at}"
            )
        except Exception as e:
            notif_logger.error(f"Could not send reminder to {u.username}: {e}")