
from pathlib import Path

def run_cleanup():
    backup_folder = Path("backups")
    max_files = 10

    all_files = sorted(
        [f for f in backup_folder.iterdir() if f.is_file()],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    files_to_delete = all_files[max_files:]

    for f in files_to_delete:
        f.unlink()
        print(f"Slettede: {f.name}")

    if not files_to_delete:
        print("Ingen filer slettet – der er 10 eller færre backups.")
