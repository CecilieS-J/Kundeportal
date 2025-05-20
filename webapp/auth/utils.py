from functools import wraps
from flask import abort
from flask_login import current_user
from webapp import db
from webapp.models import LoginHistory
from webapp.models import User  
from webapp.auth.sms import send_sms
import random
import time

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


def generate_otp():
    return str(random.randint(100000, 999999))

def handle_login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):  # bruger din eksisterende password-tjek-metode
        code = generate_otp()
        user.otp_code = code
        user.otp_timestamp = int(time.time())
        db.session.commit()
        send_sms(user.phone_number, f"Din login-kode er: {code}")
        return user
    return None

def verify_otp(user_id, otp_input):
    from time import time
    user = User.query.get(user_id)
    if user and user.otp_code == otp_input and (time() - user.otp_timestamp) < 300:
        user.otp_code = None
        user.otp_timestamp = None
        db.session.commit()
        return user
    return None