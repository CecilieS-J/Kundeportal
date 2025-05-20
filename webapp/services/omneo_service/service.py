from webapp.services.omneo_service.client import OmneoClient

class OmneoService:
    def __init__(self):
        self.client = OmneoClient()

    def fetch_member_by_id(self, customer_id: str):
        token = self.client.get_access_token(customer_id, "magento_id")
        if token:
            return self.client.get_customer_profile(token)
        return None

    def fetch_member_by_email(self, email: str):
        token = self.client.get_access_token(email, "email")
        if token:
            return self.client.get_customer_profile(token)
        return None
