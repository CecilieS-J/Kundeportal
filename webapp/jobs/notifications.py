import os
import logging
from datetime import datetime, timedelta, timezone
from .. import db
from ..models import User
from ..mail import send_alert

os.makedirs('logs', exist_ok=True)
# Logger-opsætning og funktion…


# Sørg for at logs-mappen findes
os.makedirs('logs', exist_ok=True)

# Logger til notification-jobbet
notif_logger = logging.getLogger('notifications')
notif_handler = logging.FileHandler('logs/notifications.log')
notif_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
notif_logger.addHandler(notif_handler)
notif_logger.setLevel(logging.INFO)

def remind_expiring_passwords():
    now  = datetime.now(timezone.utc)
    soon = now + timedelta(days=2)
    users = User.query.filter(User.pw_expires_at.between(now, soon)).all()

    for u in users:
        subject = "Reminder: Skift din adgangskode"
        body = (
            f"Kære {u.username},\n\n"
            f"Dit kodeord udløber den {u.pw_expires_at.strftime('%d/%m/%Y %H:%M')} UTC.\n"
            "Husk at skifte det for at bevare adgangen.\n\n"
            "Mvh. IT-support"
        )
        try:
            send_alert(subject, [u.email], body)
            notif_logger.info(f"Reminder sendt til {u.username} <{u.email}>; expires at {u.pw_expires_at}")
        except Exception as e:
            notif_logger.error(f"Kunne ikke sende reminder til {u.username}: {e}")
