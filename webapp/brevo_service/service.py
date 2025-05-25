from webapp.brevo_service.client import get_brevo_contact

class BrevoService:
    def fetch_contact(self, identifier: str) -> dict:
        raw = get_brevo_contact(identifier)
        if not raw or "email" not in raw:
            return {}
        return {
            "email":               raw.get("email", ""),
            "first_name":          raw.get("attributes", {}).get("FIRSTNAME", ""),
            "last_name":           raw.get("attributes", {}).get("LASTNAME", ""),
            "sib_id":              raw.get("id", ""),
            "subscriptions":       raw.get("listIds", []),
            "subscription_status": "subscribed" 
                                   if not raw.get("emailBlacklisted", False)
                                   else "unsubscribed",
        }
