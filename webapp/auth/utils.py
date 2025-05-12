from functools import wraps
from flask import abort
from flask_login import current_user
from webapp import db
from webapp.models import LoginHistory

def require_roles(*allowed_roles):
    """
    Decorator that restricts access to users with specific roles.
    Returns HTTP 403 if current_user.role is not in allowed_roles.
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
    """
    Records a login event with user ID and IP address in the login history.
    """
    entry = LoginHistory(user_id=user_id, ip_address=ip)
    db.session.add(entry)
    db.session.commit()
