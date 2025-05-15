from clients.omneo_client import get_omneo_contact

class OmneoService:
    def fetch_contact(self, contact_id):
        data = get_omneo_contact(contact_id)
        if not data:
            return {}
        return {
            "contact_id": data.get("id"),
            "email": data.get("email"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
        }
