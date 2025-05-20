import requests
import os
import urllib.parse

def send_sms(to: str, message: str):
    base_url = os.getenv("SMSEAGLE_URL")
    username = os.getenv("SMSEAGLE_USER")
    password = os.getenv("SMSEAGLE_PASS")
    
    encoded_message = urllib.parse.quote(message)

    full_url = (
        f"{base_url}?login={username}&pass={password}&to={to}&message={encoded_message}"
    )

    response = requests.get(full_url)
    response.raise_for_status()
    return response.text
