from flask import Blueprint

# Define blueprint‐object for authentication routes
# (login, logout, change password)
auth_bp = Blueprint(
    'auth',
    __name__,
    url_prefix='/auth',
    template_folder='templates'
)

# Import routes using a non-relative path – after auth_bp is defined
import webapp.auth.routes
