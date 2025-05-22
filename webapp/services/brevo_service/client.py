from config import settings
import requests

def get_brevo_contact(email):
    url = f'https://api.brevo.com/v3/contacts/{email}'
    headers = {
        'accept': 'application/json',
        'api-key': settings.BREVO_API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
