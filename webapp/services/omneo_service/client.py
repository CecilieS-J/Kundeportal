from config import settings
import requests
from urllib.parse import urljoin

class OmneoClient:
    def __init__(self):
        self.base_url = settings.OMNEO_BASE_URL
        self.api_token = settings.OMNEO_API_TOKEN


    def get_access_token(self, identifier: str, id_handle: str):

        url = urljoin(self.base_url + "/", "id/api/v1/auth/token")
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

        # ✅ Sæt dine print lige her:
        print("📦 Response status:", response.status_code)
        print("📦 Response content:", response.text)
        print("📦 Response headers:", response.headers)

        # 💥 Her kan den fejle, hvis svaret ikke er gyldig JSON
        try:
            token = response.json().get("token")
            print("✅ Modtaget token:", token)
            return token
        except Exception as e:
            print("❌ Kunne ikke parse JSON:", e)
            print("📦 Raw response:", response.text)
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
            print("❌ Fejl ved profil-opslag:", response.status_code, response.text)
            return None
