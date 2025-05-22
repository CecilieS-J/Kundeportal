# update_roles.py
import os, sys
from sqlalchemy import text       # ← importer text

# Sørg for, at projektroden er på modu­l-path
sys.path.insert(0, os.getcwd())

from webapp import app, db

with app.app_context():
    # 1) Byg statement som text()
    stmt = text('UPDATE "user" SET role = :new WHERE role = :old')
    params = {"new": "admin", "old": "dataansvarlig"}

    # 2) Udfør opdateringen
    res = db.session.execute(stmt, params)
    db.session.commit()

    # 3) Print resultat
    print(f"Opdaterede {res.rowcount} rækker fra 'dataansvarlig' → 'admin'.")
