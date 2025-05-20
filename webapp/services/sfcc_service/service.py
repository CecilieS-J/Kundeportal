from clients.sfcc_client import OCAPI_Authenticate_OAuth2
from webapp.services.sfcc_service.utils import get_customer, get_customer_lists
import config

class SFCCService:

     def fetch_customer_by_customer_no(self, customer_no):
        instance = "dev"
        country = "dk"
        site_id = "-"

        # Step 1: Authenticate using APIClientID
        token, _ = OCAPI_Authenticate_OAuth2(
            instance=instance,
            authType="APIClientID",
            sfcc_client_id=config.sfcc_client_id,
            sfcc_secret=config.sfcc_secret
        )

        # Step 2: Get full customer object directly (no need for second API call)
        list_id = f"mdn/customers/{customer_no}"
        customer_data = get_customer_lists(instance, config.sfcc_client_id, token, country, site_id, list_id)

        return customer_data

    
    # def fetch_customer_data(self, customer_no):
    #     instance = "dev"
    #     country = "dk"
    #     site_id = "-"
    #
    #     access_token, _ = OCAPI_Authenticate_OAuth2(
    #         instance=instance,
    #         authType="APIClientID",
    #         sfcc_client_id=config.sfcc_client_id,
    #         sfcc_secret=config.sfcc_secret
    #     )
    #
    #     list_id = f"mdn/customers/{customer_no}"
    #     customer_data = get_customer_lists(instance, config.sfcc_client_id, access_token, country, site_id, list_id)
    #
    #     customer_id = customer_data.get("customer_id")
    #     if not customer_id:
    #         return None
    #
    #     access_token, _ = OCAPI_Authenticate_OAuth2(
    #         instance=instance,
    #         authType="BusinessManager",
    #         sfcc_client_id=config.sfcc_client_id,
    #         sfcc_secret=config.sfcc_secret,
    #         sfcc_user=config.sfcc_user,
    #         sfcc_password=config.sfcc_password
    #     )
    #
    #     site_id = "DK"
    #     full_customer_data = get_customer(instance, config.sfcc_client_id, access_token, country, site_id, customer_id)
    #
    #     return full_customer_data
