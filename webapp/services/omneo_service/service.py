from clients.omneo_client import get_omneo_customer

class OmneoService:
    def fetch_customer(self, query):
        # Forsøg at hente via omneo_id først
        data = get_omneo_customer(omneo_id=query)
        if not data:
            # Hvis ikke, prøv via email
            data = get_omneo_customer(email=query)

        if not data:
            return {}

        return {
            "omneo_id": data.get("omneo_id"),
            "email": data.get("email"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "phone": data.get("phone"),
            "customer_no": data.get("customer_no"),
            "created_at": data.get("created_at"),
        }
