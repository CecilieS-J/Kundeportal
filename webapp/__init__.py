from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_talisman import Talisman
from config import settings
from datetime import datetime, timezone
from flask_apscheduler import APScheduler
from flask import Flask, redirect, url_for, request
from scripts.cli import seed_stale_user, clean_users_command, backup_command, cleanup_command, seed_admin
# Create Flask app instance
app = Flask(__name__, template_folder="templates", instance_relative_config=True)

##debug
# Set up logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add custom CLI commands
app.cli.add_command(seed_stale_user)
app.cli.add_command(clean_users_command)
app.cli.add_command(backup_command)
app.cli.add_command(cleanup_command)
app.cli.add_command(seed_admin)

# Load app configuration from settings
app.config.update({
    "SECRET_KEY": settings.SECRET_KEY,
    "SQLALCHEMY_DATABASE_URI": str(settings.DATABASE_URL),
    "SQLALCHEMY_TRACK_MODIFICATIONS": settings.SQLALCHEMY_TRACK_MODIFICATIONS,
    "PERMANENT_SESSION_LIFETIME": settings.PERMANENT_SESSION_LIFETIME,
    "SESSION_PERMANENT": settings.SESSION_PERMANENT,
    "SESSION_COOKIE_SECURE": settings.SESSION_COOKIE_SECURE,
    "SESSION_COOKIE_HTTPONLY": settings.SESSION_COOKIE_HTTPONLY,
    "REMEMBER_COOKIE_SECURE": settings.REMEMBER_COOKIE_SECURE,
    "REMEMBER_COOKIE_HTTPONLY": settings.REMEMBER_COOKIE_HTTPONLY
    
})

# Content Security Policy (CSP) configuration for Talisman
csp = {
    'default-src': ["'self'"],

    # JS-kilder + inline-scripts (Bootstrap’s data-toggle kræver 'unsafe-inline')
    'script-src': [
        "'self'",
        "cdn.jsdelivr.net",
        "code.jquery.com",
        "cdnjs.cloudflare.com",
        "maxcdn.bootstrapcdn.com",
        "'unsafe-inline'"
    ],
    # CSS-kilder + inline-styles (Bootstrap css måske med inline <style>)
    'style-src': [
        "'self'",
        "maxcdn.bootstrapcdn.com",
        "cdn.jsdelivr.net",
        "'unsafe-inline'"
    ],
    # Billeder fra egen server, data-URI’er (favicon), og CDNs
    'img-src': [
        "'self'",
        "data:",
        "cdn.jsdelivr.net",
        "maxcdn.bootstrapcdn.com"
    ],
    # Fonte fra Bootstrap CDN og JSDelivr
    'font-src': [
        "'self'",
        "maxcdn.bootstrapcdn.com",
        "cdn.jsdelivr.net"
    ],

    # Tillad egne AJAX-kald (hvis du bruger dem)
    'connect-src': ["'self'"],

    # Sæt frame til none, hvis du ikke bruger iframes
    'frame-src': ["'none'"]
}

# Enable HTTPS and security headers with Talisman
Talisman(
    app,
    content_security_policy=csp,
    force_https=True,
    strict_transport_security=True,
    strict_transport_security_max_age=31536000
)

# Redirect root URL to login page
@app.route('/')
def root():
    return redirect(url_for('auth.login'))

# Initialize database and migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Setup Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'

# Setup task scheduler with cron jobs
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

scheduler.add_job(
    id='delete_stale_users',
    func='webapp.jobs.cleanup:delete_stale_users',
    trigger='cron',
    hour=2, minute=0
)

scheduler.add_job(
    id='remind_expiring_passwords',
    func='webapp.jobs.notifications:remind_expiring_passwords',
    trigger='cron',
    hour=3, minute=0
)


# Load user from database by ID
@login_manager.user_loader
def load_user(user_id):
    from webapp.models import User
    return User.query.get(int(user_id))

# Redirect unauthorized users to login page
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login', next=request.path))

# Before every request: enforce login except for allowed endpoints and static files
@app.before_request
def require_login():
    allowed = ('auth.login', 'auth.logout', 'auth.change_password','auth.verify_otp_route','auth.activate')
    is_static = (
        request.endpoint == 'static' or
        (request.endpoint and request.endpoint.endswith('.static'))
    )

    # If not logged in, redirect to login page
    if not current_user.is_authenticated and request.endpoint not in allowed and not is_static:
        return redirect(url_for('auth.login', next=request.path))

    # If logged in, check if password needs to be changed
    if current_user.is_authenticated:
        expires = current_user.pw_expires_at  

        # If no expiration date is set → force password change
        if expires is None:
            needs_change = True
        else:
             # If datetime is naive → assume UTC timezone
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            needs_change = expires <= datetime.now(timezone.utc)

         # If password MUST be changed and not already on change-password page
        if needs_change and request.endpoint not in allowed:
            return redirect(url_for('auth.change_password', next=request.path))
    
# Make UserRole available in templates
@app.context_processor
def inject_user_role():
    from webapp.models import UserRole
    return dict(UserRole=UserRole)


# Import and register blueprints in desired order
from webapp.auth         import auth_bp
from webapp.admin        import admin_bp
from webapp.external_customer_service.routes import external_customer_service_bp
from webapp.routes       import public_bp
from webapp.brevo_service import brevo_service_bp
from webapp.sfcc_service import sfcc_service_bp
from webapp.omneo_service import omneo_service_bp
from comparison.routes import comparison_bp

app.register_blueprint(comparison_bp)
app.register_blueprint(omneo_service_bp)
app.register_blueprint(sfcc_service_bp)
app.register_blueprint(brevo_service_bp)
app.register_blueprint(auth_bp)           
app.register_blueprint(admin_bp)          
app.register_blueprint(external_customer_service_bp)   
app.register_blueprint(public_bp)         

