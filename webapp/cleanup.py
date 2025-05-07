# webapp/cleanup.py

from datetime import datetime, timedelta, timezone
from webapp import db
from webapp.models import User

def delete_stale_users():
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    stale = User.query.filter(User.pw_changed_at < cutoff).all()
    count = len(stale)
    for u in stale:
        db.session.delete(u)
    db.session.commit()
    print(f"Deleted {count} stale users")
