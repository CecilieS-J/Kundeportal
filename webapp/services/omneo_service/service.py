from webapp.services.omneo_service.client import OmneoClient

class OmneoService:
    def __init__(self):
        self.client = OmneoClient()

    def _extract_profile_data(self, profile):
        identities = {i["handle"]: i["identifier"] for i in profile.get("identities", [])}
        return {
            "id": profile.get("id"),
            "first_name": profile.get("first_name"),
            "last_name": profile.get("last_name"),
            "email": profile.get("email"),
            "phone": profile.get("mobile_phone"),
            "gender": profile.get("gender"),
            "card_pos": identities.get("card_pos"),
            "sfcc_id": identities.get("sfcc_id"),
            "sib_id": identities.get("sib_id"),
        }

    def fetch_by_email(self, email):
        raw = self.client.get_profiles_by_email(email)
        profiles = raw.get("data", []) if isinstance(raw, dict) else []
        return [self._extract_profile_data(p) for p in profiles]

    def fetch_by_card_pos(self, card_pos):
        raw = self.client.get_profiles_by_card_pos(card_pos)
        profiles = raw.get("data", []) if isinstance(raw, dict) else []
        return [self._extract_profile_data(p) for p in profiles]

    def fetch_top_profiles(self, limit=10):
        raw = self.client.get_profiles(limit=limit)
        profiles = raw.get("data", []) if isinstance(raw, dict) else []
        return [self._extract_profile_data(p) for p in profiles]

    def fetch_profile_by_id(self, profile_id):
        raw = self.client.get_profile_by_id(profile_id)
        profile = raw.get("data") if isinstance(raw, dict) else None
        return self._extract_profile_data(profile) if profile else None
    



    
   


