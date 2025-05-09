import os
import logging
import requests

# Sæt en logger op, der skriver til standard output
logger = logging.getLogger("mailgun")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def send_alert(subject, recipients, text=None, html=None):
    domain  = os.getenv('MAILGUN_DOMAIN')
    api_key = os.getenv('MAILGUN_API_KEY')
    resp = requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from":    f"Kundeportal <postmaster@{domain}>",
            "to":      recipients,
            "subject": subject,
            **({"text": text}   if text else {}),
            **({"html": html}   if html else {}),
        }
    )
    resp.raise_for_status()
    return resp
