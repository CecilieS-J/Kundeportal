from webapp.brevo_service.client import get_brevo_contact

class BrevoService:
    def fetch_contact(self, identifier):
        """
        Hent en Brevo-kontakt ved hjælp af e-mail eller SIB ID.
        """
        data = get_brevo_contact(identifier)

        if not data:
            return {}

        return {
            "email": data.get("email", ""),
            "first_name": data.get("attributes", {}).get("FIRSTNAME", ""),
            "last_name": data.get("attributes", {}).get("LASTNAME", ""),
            "sib_id": data.get("id", ""),
            "subscriptions": data.get("listIds", []),
            "subscription_status": "subscribed" if not data.get("emailBlacklisted", False) else "unsubscribed"
        }