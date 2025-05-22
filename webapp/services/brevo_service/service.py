from webapp.services.brevo_service.client import get_brevo_contact

class BrevoService:
    def fetch_contact(self, query):
        """
        Look up a Brevo contact by email or SIB ID (Brevo API finder selv ud af det)
        """
        data = get_brevo_contact(query)

        if not data:
            return {}

        return {
            "email": data.get("email"),
            "first_name": data.get("attributes", {}).get("FIRSTNAME"),
            "last_name": data.get("attributes", {}).get("LASTNAME"),
            "sib_id": data.get("id"),
            "subscriptions": data.get("listIds", []),
            "subscription_status": "subscribed" if not data.get("emailBlacklisted") else "unsubscribed"
        }
