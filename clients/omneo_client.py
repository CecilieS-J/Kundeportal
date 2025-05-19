import requests
from config import settings

def get_omneo_customer(omneo_id=None, email=None):
    url = f"{settings.OMNEO_BASE_URL}/customers"

    headers = {
        "Authorization": f"Bearer {settings.OMNEO_API_KEY}",
        "Accept": "application/json"
    }

    params = {}
    if omneo_id:
        params["omneo_id"] = omneo_id
    if email:
        params["email"] = email

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        # Hvis det er en liste med kunder, tag den første
        data = response.json()
        if isinstance(data, list) and data:
            return data[0]
        return data

    print(f"Omneo customer lookup failed: {response.status_code} {response.text}")
    return None
