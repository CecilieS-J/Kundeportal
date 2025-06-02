import os
import shutil
import logging
from datetime import datetime

# Opret en logger for vedligeholdelses-scripts
logger = logging.getLogger('maintenance.backup')

def run_backup():
    """
    Copier SQLite-databasen til en timestamped backup-fil
    og logger processen i stedet for at printe.
    """
    db_path = os.path.join("instance", "customer_data.db")
    backup_dir = "backups"

    # Debug-oplysninger om sti og nuværende mappe
    logger.debug("Current working directory: %s", os.getcwd())
    logger.debug("Looking for DB at: %s", os.path.abspath(db_path))

    # Tjek om databasefilen eksisterer
    if not os.path.exists(db_path):
        logger.error("❌ FEJL: Kan ikke finde databasefilen: %s", os.path.abspath(db_path))
        return

    # Opret backup-mappen hvis den ikke findes
    os.makedirs(backup_dir, exist_ok=True)

    # Lav en tidsstemplet backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"customer_data_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)

    try:
        shutil.copy2(db_path, backup_path)
        logger.info("✅ Backup gemt som: %s", backup_path)
    except Exception as e:
        # logger.exception() medtager stack trace
        logger.exception("❌ FEJL i run_backup(): %s", e)
