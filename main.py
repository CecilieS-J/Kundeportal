# main.py

import os
import logging
from webapp import app
from backup_script import lav_backup  # Function to create DB backup
from scripts.cli import seed_admin
app.cli.add_command(seed_admin)


# Configure logging
logging.basicConfig(level=logging.DEBUG)


def test_sfcc():
    import json
    print("🔧 Running SFCC test...")

    # Settings og credentials
    from config import sfcc_client_id, sfcc_secret, sfcc_user, sfcc_password, sfcc_instance
    from webapp.services.sfcc_service.utils import get_customer_lists  # Vi bruger kun dette
    from clients.sfcc_client import OCAPI_Authenticate_OAuth2

    instance = "dev"
    country = "dk"
    site_id = "-"
    customer_no = "00258536"
    list_id = f"mdn/customers/{customer_no}"

    # Step 1: Hent token via APIClientID
    token, message = OCAPI_Authenticate_OAuth2(
        instance=instance,
        authType="APIClientID",
        sfcc_client_id=sfcc_client_id,
        sfcc_secret=sfcc_secret
    )
    print(f"🔐 Token (ClientID): {token}")
    print(f"ℹ️ {message}")

    # Step 2: Lookup på customer_id og alt anden relevant data
    customer_data = get_customer_lists(instance, sfcc_client_id, token, country, site_id, list_id)

    print("📄 Full customer_data from get_customer_lists():")
    print(json.dumps(customer_data, indent=2))

    # Udtræk specifikke felter
    summary = {
        "customer_id": customer_data.get("customer_id"),
        "customer_no": customer_data.get("customer_no"),
        "email": customer_data.get("email"),
        "first_name": customer_data.get("first_name"),
        "last_name": customer_data.get("last_name"),
        "birthday": customer_data.get("birthday"),
        "phone": customer_data.get("phone_home"),
        "goodieCardNumber": customer_data.get("c_goodieCardNumber"),
        "goodieTierLevel": customer_data.get("c_goodieTierLevel"),
        "omneoMemberID": customer_data.get("c_omneoMemberID"),
        "last_login_time": customer_data.get("last_login_time")
    }

    print("\n👤 SFCC Customer Summary:")
    print(json.dumps(summary, indent=2))

    # Step 3 og 4 er midlertidigt udkommenteret, da de fejler med 403:
    #
    # token, message = OCAPI_Authenticate_OAuth2(
    #     instance=instance,
    #     authType="BusinessManager",
    #     sfcc_client_id=sfcc_client_id,
    #     sfcc_secret=sfcc_secret,
    #     sfcc_user=sfcc_user,
    #     sfcc_password=sfcc_password
    # )
    # print(f"🔐 Token (BusinessManager): {token}")
    # print(f"ℹ️ {message}")
    #
    # site_id = "DK"
    # full_data = get_customer(instance, sfcc_client_id, token, country, site_id, customer_id)
    #
    # print("👤 SFCC Customer Result:")
    # print(full_data)


def test_omneo():
    from webapp.services.omneo_service.service import OmneoService  

    service = OmneoService()

    # Test med GoodieCard ID
    customer_id = "83017843"
    result = service.fetch_member_by_id(customer_id)
    print("GoodieCard result:", result)

    # Test med e-mail
    email = "magasintest+blocked@protonmail.com"
    result = service.fetch_member_by_email(email)
    print("Email result:", result)

        
def main():
    """
    Main entry point for running the Flask application.
    Shows all endpoints, starts the server, and handles backup on shutdown.
    """

    # Show available Flask URL routes in terminal
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} -> {rule}")

    # Run optional test to verify SFCC integration or Omneo works
    #test_sfcc()
    #test_omneo()

     
    try:
        
        # Start Flask development server
        app.run(host='127.0.0.1', port=80, debug=True)

    finally:
        # Only run backup when the actual reloader process exits
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            print("📦 Application shutting down. Creating backup...")
            lav_backup()


# Only run if executed directly (not when imported as module)
if __name__ == "__main__":
    main()
