import os

def run_cleanup():
    backup_dir = "backups"
    max_backups = 10

    backups = sorted(
        [f for f in os.listdir(backup_dir)
         if f.endswith(".db")],
        reverse=True
    )

    if len(backups) > max_backups:
        to_delete = backups[max_backups:]
        for filename in to_delete:

            # 🛑 Sikkerhedstjek: slet aldrig den aktive database
            if filename == "customer_data.db":
                continue  # spring over, må ikke slettes

            full_path = os.path.join(backup_dir, filename)
            os.remove(full_path)
            print(f"Slettede backup: {filename}")
    else:
        print("Ingen filer slettet – der er 10 eller færre backups.")
