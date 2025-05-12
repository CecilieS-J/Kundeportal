import sqlite3
import os
from datetime import datetime

def lav_backup(db_filnavn='customer_data.db', instance_folder='instance', backup_folder='backups'):
    """
    Tager en backup af en SQLite database og gemmer den i en backups-mappe med timestamp.
    
    Args:
        db_filnavn (str): Navnet på databasefilen (default: 'customer_data.db').
        instance_folder (str): Mappen hvor den originale database ligger (default: 'instance').
        backup_folder (str): Mappen hvor backups gemmes (default: 'backups').
    """

    # Find stien til den originale database
    db_path = os.path.join(os.path.dirname(__file__), instance_folder, db_filnavn)

    if not os.path.exists(db_path):
        print(f"FEJL: Kan ikke finde databasefilen: {db_path}")
        return

    # Opret backups-mappen hvis den ikke findes
    backup_dir = os.path.join(os.path.dirname(__file__), backup_folder)
    os.makedirs(backup_dir, exist_ok=True)

    # Lav filnavn med timestamp til backup-filen
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'{db_filnavn.split(".")[0]}_backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_filename)

    # Udfør backup
    try:
        source_conn = sqlite3.connect(db_path)
        backup_conn = sqlite3.connect(backup_path)

        with backup_conn:
            source_conn.backup(backup_conn)

        print(f'✅ Backup gemt som: {backup_path}')
    except sqlite3.Error as e:
        print(f"FEJL under backup: {e}")
    finally:
        source_conn.close()
        backup_conn.close()
