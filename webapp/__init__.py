# webapp/__init__.py

from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_talisman import Talisman
from config import Config
from datetime import datetime, timezone


#Opret app
app = Flask(__name__, template_folder="templates")
app.config.from_object(Config)

# Konfiguration af CSP (eksempel)

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

Talisman(
    app,
    content_security_policy=csp,
    force_https=True,
    strict_transport_security=True,
    strict_transport_security_max_age=31536000
)


#Rute for roden – altid login
@app.route('/')
def root():
    return redirect(url_for('auth.login'))

#Database + migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'

#User-loader (import User indeni for at undgå cirkler)
@login_manager.user_loader
def load_user(user_id):
    from webapp.models import User
    return User.query.get(int(user_id))

#Uautoriseret adgang → login
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login', next=request.path))

#Globalt før-request: kun auth & static er offentligt

@app.before_request
@app.before_request
def require_login():
    allowed = ('auth.login', 'auth.logout', 'auth.change_password')
    is_static = (
        request.endpoint == 'static' or
        (request.endpoint and request.endpoint.endswith('.static'))
    )

    # 1) Hvis ikke logget ind → login
    if not current_user.is_authenticated and request.endpoint not in allowed and not is_static:
        return redirect(url_for('auth.login', next=request.path))

    # 2) Hvis logget ind → tjek om password skal skiftes
    if current_user.is_authenticated:
        expires = current_user.pw_expires_at  # <— defineres her, også hvis None

        # Hvis ingen udløbsdato → tving til skift
        if expires is None:
            needs_change = True
        else:
            # Hvis naive datetime → antag UTC
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            needs_change = expires <= datetime.now(timezone.utc)

        # Hvis password SKAL skiftes, og du ikke allerede er på change-password:
        if needs_change and request.endpoint not in allowed:
            return redirect(url_for('auth.change_password', next=request.path))
    

#Gør UserRole tilgængelig i templates
@app.context_processor
def inject_user_role():
    from webapp.models import UserRole
    return dict(UserRole=UserRole)

#Importér modeller, så SQLAlchemy kender dem
import webapp.models

# 10) Importér blueprints
from webapp.auth         import auth_bp
from webapp.admin        import admin_bp
from webapp.completeness import completeness_bp
from webapp.routes       import public_bp

#Registrér blueprints i ønsket rækkefølge
app.register_blueprint(auth_bp)           # login/logout
app.register_blueprint(admin_bp)          # /admin/*
app.register_blueprint(completeness_bp)   # /completeness/*
app.register_blueprint(public_bp)         # fx /barcodes
