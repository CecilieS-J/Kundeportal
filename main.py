# main.py

import os
import logging
from webapp import app
from backup_script import lav_backup  # Function to create DB backup
from config import settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def test_sfcc():
    """
    Optional test: Run SFCC token and customer lookup before starting the server.
    Useful to verify API credentials work correctly.
    """
    from clients.sfcc_client import get_sfcc_token, get_sfcc_customer

    logging.info("Running SFCC test...")

    token = get_sfcc_token()
    print("🔐 Access Token:", token)

    # Replace with a valid customer ID for testing
    customer_id = "00258536"
    result = get_sfcc_customer(customer_id)

    print("👤 SFCC Customer Result:")
    print(result)


def main():
    """
    Main entry point for running the Flask application.
    Shows all endpoints, starts the server, and handles backup on shutdown.
    """

    # Show available Flask URL routes in terminal
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} -> {rule}")

    # Run optional test to verify SFCC integration works
    test_sfcc()

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
