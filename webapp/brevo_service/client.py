from config import settings
import requests

def get_brevo_contact(identifier):
    """
    Hent en kontakt fra Brevo ved hjælp af e-mail eller SIB ID.
    """
    url = f'https://api.brevo.com/v3/contacts/{identifier}'
    headers = {
        'accept': 'application/json',
        'api-key': settings.BREVO_API_KEY
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None
    except requests.RequestException as e:
        print(f"Fejl ved API-kald: {e}")
        return None