from clients.sfcc_client import get_sfcc_token, get_sfcc_customer

class SFCCService:
    def fetch_customer(self, customer_id):
        token = get_sfcc_token()
        if not token:
            return {}
        data = get_sfcc_customer(customer_id, token)
        if not data:
            return {}
        return {
            "customer_id": data.get("customer_no"),
            "email": data.get("email"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
        }
