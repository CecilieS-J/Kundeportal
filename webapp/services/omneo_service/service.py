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
            "sfcc_customer": identities.get("sfcc_customer", None),
            
        }

    def fetch_by_email(self, email):
        try:
            profiles = self.client.get_profiles_by_email(email)
            return [self._extract_profile_data(p) for p in profiles if p.get("email", "").lower() == email.lower()]
        except Exception as e:
            print(f"Fejl ved søgning efter email {email}: {e}")
            return []

    def fetch_by_card_pos(self, card_pos):
        profiles = self.client.get_profiles_by_card_pos(card_pos)
        return [self._extract_profile_data(p) for p in profiles] if profiles else []

    def fetch_top_profiles(self, limit=10):
        try:
            raw = self.client.get_profiles(limit=limit)
            profiles = raw.get("data", []) if isinstance(raw, dict) else []
            return [self._extract_profile_data(p) for p in profiles]
        except Exception as e:
            print(f"Fejl ved hentning af profiler: {e}")
            return []

    def fetch_profile_by_id(self, profile_id):
        try:
            raw = self.client.get_profile_by_id(profile_id)
            profile = raw.get("data") if isinstance(raw, dict) else None
            return self._extract_profile_data(profile) if profile else None
        except Exception as e:
            print(f"Fejl ved hentning af profil {profile_id}: {e}")
            return None
    

   