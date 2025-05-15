from config import settings
import requests

def get_omneo_contact(contact_id):
    url = f'{settings.OMNEO_BASE_URL}/contacts/{contact_id}'
    headers = {
        'Authorization': f'Bearer {settings.OMNEO_API_KEY}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
