from webapp.brevo_service.client import get_brevo_contact

class BrevoService:
    def fetch_contact(self, identifier: str) -> dict:
        raw = get_brevo_contact(identifier)
        if not raw or "email" not in raw:
            return {}
        attrs = raw.get("attributes", {})
        return {
            "email":               raw.get("email", ""),
            "first_name":          attrs.get("FIRSTNAME", ""),
            "last_name":           attrs.get("LASTNAME", ""),
            "sib_id":              raw.get("id", ""),
            "goodiecard":          attrs.get("GOODIE_ID", ""),
            "omneo_id":            None,
            "customer_no": attrs.get("CUSTOMER_NO", ""),
            "sib_id":              raw.get("id", ""),
            "phone_home":          attrs.get("PHONE", ""),
            "phone_mobile":        attrs.get("SMS", ""),
            "subscriptions":       raw.get("listIds", []),
            "subscription_status": "subscribed" 
                                   if not raw.get("emailBlacklisted", False)
                                   else "unsubscribed",
        }
