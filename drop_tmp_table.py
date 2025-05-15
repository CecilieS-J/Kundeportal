# drop_tmp_table.py

from webapp import app, db
from sqlalchemy import text

with app.app_context():
    # Brug en transaktion, så DDL også bliver committet
    with db.engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS _alembic_tmp_user;"))
    print("✅ _alembic_tmp_user dropped successfully")
