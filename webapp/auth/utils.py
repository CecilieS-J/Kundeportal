from functools import wraps
from flask import abort
from flask_login import current_user
from webapp import db
from webapp.models import LoginHistory

def require_roles(*allowed_roles):
    """
    Dekorator, der kun tillader endpoints for current_user.role i allowed_roles.
    Ellers HTTP 403.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if (not current_user.is_authenticated
                or current_user.role not in allowed_roles):
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def record_login(user_id, ip):
    entry = LoginHistory(user_id=user_id, ip_address=ip)
    db.session.add(entry)
    db.session.commit()
