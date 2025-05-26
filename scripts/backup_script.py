import os
import shutil
from datetime import datetime

def run_backup():
    # Define the path to the database and the backup directory
    db_path = os.path.join("instance", "customer_data.db")  
    backup_dir = "backups"

  
    print("🔍 Current dir:", os.getcwd())
    print("🔍 Leder efter DB på:", os.path.abspath(db_path))

    if not os.path.exists(db_path):
        print(f"❌ FEJL: Kan ikke finde databasefilen: {os.path.abspath(db_path)}")
        return

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"customer_data_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)

    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup gemt som: {backup_path}")
