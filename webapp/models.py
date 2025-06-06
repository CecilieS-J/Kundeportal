# webapp/models.py

from webapp import db
from flask_login import UserMixin
import enum
from datetime import datetime, timedelta, timezone
from sqlalchemy.dialects.sqlite import JSON
from werkzeug.security import check_password_hash

class UserRole(enum.Enum):
    admin         = "admin"
    it_supporter  = "it_supporter"
    watcher       = "watcher"

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(128), nullable=True)
    role          = db.Column(db.Enum(UserRole), nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    pw_changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    pw_expires_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=14)
    )
    otp_code = db.Column(db.String(6), nullable=True)
    otp_timestamp = db.Column(db.Integer, nullable=True)

    ##MFA
    secret_token = db.Column(db.String(64), nullable=True)
    secret_token_expires_at = db.Column(db.DateTime, nullable=True)
    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    __tablename__ = 'customer'
    id          = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(64), unique=True, nullable=False)
    name        = db.Column(db.String(120))
    email       = db.Column(db.String(120))

class ExternalSystem(db.Model):
    __tablename__ = 'external_system'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

class CheckRun(db.Model):
    __tablename__ = 'check_run'
    id           = db.Column(db.Integer, primary_key=True)
    run_type     = db.Column(db.String(64), nullable=False)
    timestamp    = db.Column(db.DateTime, server_default=db.func.now())
    initiated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class CheckResult(db.Model):
    __tablename__ = 'check_result'
    id            = db.Column(db.Integer, primary_key=True)
    check_run_id  = db.Column(db.Integer, db.ForeignKey('check_run.id'), nullable=False)
    customer_id   = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    system_id     = db.Column(db.Integer, db.ForeignKey('external_system.id'), nullable=False)
    status        = db.Column(db.String(64), nullable=False)
    details       = db.Column(JSON)

class LoginHistory(db.Model):
    __tablename__ = 'login_history'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ip_address   = db.Column(db.String)
    user         = db.relationship('User', backref='login_history')


def check_password(self, password):
    if self.password_hash is None:
        return False
    return check_password_hash(self.password_hash, password)