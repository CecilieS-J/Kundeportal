# Import necessary libraries
import os
from webapp import app
from backup_script import lav_backup  # Import your backup function

def main():
    # (Optional) Print all URL endpoints for a quick overview
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} -> {rule}")

    try:
        # Start the development server
        app.run(host='127.0.0.1', port=80, debug=True)
        # app.run(host='0.0.0.0', port=80, debug=True)  # Uncomment for external access
    finally:
        # Only create backup when running in the actual reloader process (not the first debug spawn)
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            print("Closing app... creating database backup.")
            lav_backup()

# This ensures the main() function runs only when this script is executed directly,
# not when it's imported as a module elsewhere.
if __name__ == "__main__":
    main()
