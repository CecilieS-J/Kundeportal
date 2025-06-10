import os
import logging

def run_cleanup():

    
    backup_dir = "backups"
    max_backups = 10

    # Get all backup files ending with .db, sorted newest first
    backups = sorted(
        [f for f in os.listdir(backup_dir)
         if f.endswith(".db")],
        reverse=True
    )


    # If there are more than the allowed number of backups, delete the oldest
    if len(backups) > max_backups:
        to_delete = backups[max_backups:]
        for filename in to_delete:

            # Safety check so it never delets the active database
            if filename == "customer_data.db":
                continue  # skip

            full_path = os.path.join(backup_dir, filename)
            os.remove(full_path)
            logging.info(f"Deleted backup: {filename}")
    else:
        logging.info("No files deleted – 10 or fewer backups present.")
