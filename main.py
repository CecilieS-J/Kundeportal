import os
from webapp import app
from scripts.backup_script import run_backup
from scripts.cleanup_backups import run_cleanup
import logging
#import scripts.smoke_tests as smoke_tests

# global logging-opsætning
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)



        
def main():
    """
    Main entry point for running the Flask application.
    Shows all endpoints, starts the server, and handles backup on shutdown.
    """

    # Show available Flask URL routes in terminal
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} -> {rule}")

    # Run optional test to verify SFCC integration or Omneo works
    #smoke_tests.test_sfcc()
    #smoke_tests.test_omneo()
    #smoke_tests.test_omneo_email()
    #smoke_tests.test_omneo_card_pos()
    

     
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
