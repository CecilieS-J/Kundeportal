# scripts/inspect_db.py
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from webapp import app, db
from sqlalchemy import inspect, text

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tabeller i app'ens database:", tables)

    for table in tables:
        print(f"\nIndhold af `{table}`:")
        # Brug text() om SQL’en
        try:
            rows = db.session.execute(text(f"SELECT * FROM {table}")).fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print(f"  Kunne ikke læse `{table}`: {e}")
