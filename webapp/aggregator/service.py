from webapp.services.external_customer_service.service import CustomerExternalService
from webapp.services.brevo_service.service import BrevoService
from webapp.services.sfcc_service.service import SFCCService
from webapp.services.omneo_service.service import OmneoService

class CustomerAggregatorService:
    def compare_customer_profile(self, goodie_id):
        mdm_data = CustomerExternalService().fetch_external_customer(goodie_id=goodie_id)
        if not mdm_data:
            return {"error": "Customer not found in MDM"}

        brevo_data = BrevoService().fetch_contact(mdm_data.get("email"))
        sfcc_data = SFCCService().fetch_customer(mdm_data.get("customer_no"))
        omneo_data = OmneoService().fetch_contact(mdm_data.get("omneo_id"))

        return {
            "first_name": {
                "MDM": mdm_data.get("first_name"),
                "Brevo": brevo_data.get("first_name"),
                "SFCC": sfcc_data.get("first_name"),
                "Omneo": omneo_data.get("first_name"),
            },
            "last_name": {
                "MDM": mdm_data.get("last_name"),
                "Brevo": brevo_data.get("last_name"),
                "SFCC": sfcc_data.get("last_name"),
                "Omneo": omneo_data.get("last_name"),
            },
            "email": {
                "MDM": mdm_data.get("email"),
                "Brevo": brevo_data.get("email"),
                "SFCC": sfcc_data.get("email"),
                "Omneo": omneo_data.get("email"),
            },
            "customer_no": {
                "MDM": mdm_data.get("customer_no"),
                "SFCC": sfcc_data.get("customer_id"),
            },
            "sib_id": {
                "MDM": mdm_data.get("sib_id"),
                "Brevo": brevo_data.get("sib_id"),
            }
        }
