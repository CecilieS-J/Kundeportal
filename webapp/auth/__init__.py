# webapp/auth/__init__.py

from flask import Blueprint

# Definer blueprint‐objektet først
auth_bp = Blueprint(
    'auth',
    __name__,
    url_prefix='/auth',
    template_folder='templates/auth'
)

# Importér routes med en *ikke-relativ* sti – efter auth_bp er defineret
import webapp.auth.routes
