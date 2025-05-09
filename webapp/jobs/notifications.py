import os
import logging
from datetime import datetime, timedelta, timezone
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
    """
    Sender reminder til brugere, hvis sidste password-skrift:
      - er mindst 48 timer siden, og
      - er maksimum 14 dage siden (ellers slettes de snart).
    """
    now = datetime.now(timezone.utc)
    # Kun de, som har skiftet for mindst 48 timer siden
    remind_threshold = now - timedelta(hours=48)
    # Og som er under 14 dage gamle
    delete_threshold = now - timedelta(days=14)

    users = User.query.filter(
        User.pw_changed_at <= remind_threshold,
        User.pw_changed_at > delete_threshold
    ).all()

    for u in users:
        subject = "Reminder: Skift din adgangskode"
        body = (
            f"Kære {u.username},\n\n"
            f"Du skiftede dit kodeord den {u.pw_changed_at.strftime('%d/%m/%Y %H:%M')} UTC.\n"
            "Det er nu over 48 timer siden. For din egen sikkerhed bør du skifte det igen senest om 14 dage.\n\n"
            "Mvh. IT-support"
        )
        try:
            send_alert(subject, [u.email], body)
            notif_logger.info(
                f"Reminder sendt til {u.username} <{u.email}>; pw_changed_at={u.pw_changed_at}"
            )
        except Exception as e:
            notif_logger.error(f"Kunne ikke sende reminder til {u.username}: {e}")