import os
from webapp import app
from scripts.backup_script import run_backup
from scripts.cleanup_backups import run_cleanup
import logging

# global logging-opsætning
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)


def test_sfcc():
    import json
    print("🔧 Running SFCC test...")

    # Settings og credentials
    from config import sfcc_client_id, sfcc_secret
    from webapp.sfcc_service.utils import get_customer_lists  
    from webapp.sfcc_service.client import OCAPI_Authenticate_OAuth2

    instance = "dev"
    country = "dk"
    site_id = "-"
    customer_no = "00258536"
    list_id = f"mdn/customers/{customer_no}"

    # Step 1: Get token from APIClientID
    token, message = OCAPI_Authenticate_OAuth2(
        instance=instance,
        authType="APIClientID",
        sfcc_client_id=sfcc_client_id,
        sfcc_secret=sfcc_secret
    )
    print(f"🔐 Token (ClientID): {token}")
    print(f"ℹ️ {message}")

    # Step 2: Lookup on customer_id and others of relevance
    customer_data = get_customer_lists(instance, sfcc_client_id, token, country, site_id, list_id)

    print("📄 Full customer_data from get_customer_lists():")
    print(json.dumps(customer_data, indent=2))

    # Specifikc fields of customer data to get output
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

    # Step 3 og 4 er midlertidigt udkommenteret, da de fejler med 403 grundet manglende tilladelser:
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
    from webapp.omneo_service.service import OmneoService  

    service = OmneoService()

    # Test med GoodieCard ID
    customer_id = "83017843"
    result = service.fetch_by_card_pos(customer_id)
    print("GoodieCard result:", result)

    # Test med e-mail
    email = "magasintest+blocked@protonmail.com"
    result = service.fetch_by_email(email)
    print("Email result:", result)


def test_omneo_email():
    import os
    import json
    import requests
    from dotenv import load_dotenv

    print("🔧 Running Omneo Email test...")

    # Indlæs variabler fra .env
    load_dotenv()
    token = os.getenv("OMNEO_API_TOKEN")
    base_url = os.getenv("OMNEO_BASE_URL")

    if not token or not base_url:
        print("❌ Mangler OMNEO_API_TOKEN eller OMNEO_BASE_URL. Tjek .env-filen.")
        return

    # Input
    email = "magasintest+blocked@protonmail.com"  # Udskift med reel test-email

    # Request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{base_url}/profiles?email={email}"
    response = requests.get(url, headers=headers)

    # Output
    if response.status_code == 200:
        print("✅ Brugerdata:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ Fejl ved hentning af brugerdata:", response.status_code, response.text)

  
def test_omneo_card_pos():
    import os
    import json
    import requests
    from dotenv import load_dotenv

    print("🔧 Running Omneo GoodieCard test...")

    # Indlæs variabler fra .env
    load_dotenv()
    token = os.getenv("OMNEO_API_TOKEN")
    base_url = os.getenv("OMNEO_BASE_URL")

    if not token or not base_url:
        print("❌ Mangler OMNEO_API_TOKEN eller OMNEO_BASE_URL. Tjek .env-filen.")
        return

    # Input
    card_pos = "83017843"  

    # Request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{base_url}/profiles?card_pos={card_pos}"
    response = requests.get(url, headers=headers)

    # Output
    if response.status_code == 200:
        print("✅ Brugerdata:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ Fejl:", response.status_code, response.text)

        
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
    #test_omneo_email()
    #test_omneo_card_pos()

     
    try:
        
        # Start Flask development server
        app.run(host='127.0.0.1', port=80, debug=True)

    finally:
        
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            print("📦 Application shutting down. Starting backup and cleanup...")

            # Run backup
            run_backup()
            
             
            # Run cleanup
            try:
              print("🧹 Kører oprydning af gamle backups...")
              run_cleanup()
              print("✅ Cleanup gennemført.")
            except Exception as e:
               print(f"❌ FEJL i run_cleanup(): {e}")

            print("🏁 Backup og oprydning afsluttet.")



# Only run if executed directly (not when imported as module)
if __name__ == "__main__":
    main()
