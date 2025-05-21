from config import settings
import requests
from urllib.parse import urljoin

class OmneoClient:
    def __init__(self):
        self.base_url = settings.OMNEO_BASE_URL
        self.api_token = settings.OMNEO_API_TOKEN


    def get_access_token(self, identifier: str, id_handle: str):
        url = urljoin(self.base_url + "/", "auth/token")
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "id": identifier,
            "id_handle": id_handle
        }

        print("📡 Kald til URL:", url)
        response = requests.post(url, headers=headers, json=payload)

        print("Response status:", response.status_code)
        print("Response content:", response.text)
        print("Response headers:", response.headers)

        try:
            token = response.json().get("token")
            print("✅ Modtaget token:", token)
            return token
        except Exception as e:
            print("Kunne ikke parse JSON:", e)
            print("Raw response:", response.text)
            return None

    def get_customer_profile(self, token: str):
        url = f"{self.base_url}/profiles/me"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print("Fejl ved profil-opslag:", response.status_code, response.text)
            return None

    def get_profiles_by_email(self, email: str):
        url = f"{self.base_url}/profiles?email={email}"
        return self._get(url).get("data", [])  # <- Tilføj .get("data", []) her

    def get_profiles_by_card_pos(self, card_pos: str):
        url = f"{self.base_url}/profiles?card_pos={card_pos}"
        return self._get(url).get("data", [])

    def get_profile_by_id(self, profile_id: str):
        url = f"{self.base_url}/profiles/{profile_id}"
        return self._get(url)

    def _get(self, url):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print("Fejl ved GET-kald:", response.status_code, response.text)
            return None


    def get_profiles(self, limit=10):
          url = f"{self.base_url}/profiles?limit={limit}"
          return self._get(url)

