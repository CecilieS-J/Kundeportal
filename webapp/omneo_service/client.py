from config import settings
import requests
from urllib.parse import quote

class OmneoClient:
    def __init__(self):
        self.base_url = settings.OMNEO_BASE_URL
        self.api_token = settings.OMNEO_API_TOKEN

    def _get(self, url):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        print("➡️ Request URL:", url)
        response = requests.get(url, headers=headers)
        print("📦 Status:", response.status_code)
        print("📦 Body:", response.text)
        try:
            return response.json()
        except Exception as e:
            print("❌ JSON-fejl:", e)
            return {}

    def _post(self, url, payload):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        print("➡️ Request URL:", url)
        print("➡️ Payload:", payload)
        try:
            response = requests.post(url, json=payload, headers=headers)
            print("📦 Status:", response.status_code)
            print("📦 Body:", response.text)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"❌ HTTP-fejl: {http_err}, Status: {response.status_code}, Body: {response.text}")
            return {}
        except requests.exceptions.RequestException as req_err:
            print(f"❌ Netværksfejl: {req_err}")
            return {}
        except ValueError as json_err:
            print(f"❌ JSON-fejl: {json_err}, Body: {response.text}")
            return {}

    def get_profiles_by_email(self, email: str):
        url = f"{self.base_url}/profiles?filter[email]={quote(email)}"
        return self._get(url).get("data", [])

    def get_profiles_by_card_pos(self, card_pos: str):
        url = f"{self.base_url}/profiles/search-id"
        payload = {"type": "card_pos", "id": card_pos}
        response = self._post(url, payload)
        return [response.get("data")] if response.get("data") else []

    def get_profiles(self, limit=10):
        url = f"{self.base_url}/profiles?limit={limit}"
        return self._get(url)

    def get_profile_by_id(self, profile_id: str):
        url = f"{self.base_url}/profiles/{profile_id}"
        return self._get(url)