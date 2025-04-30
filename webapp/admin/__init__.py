# webapp/admin/__init__.py

from flask import Blueprint

# 1) Definér blueprint
admin_bp = Blueprint(
    'admin',                # giver endpoints som admin.list_users, admin.create_user…
    __name__,
    url_prefix='/admin',    # alle ruter bliver /admin/…
    template_folder='templates/admin'
)

# 2) Importér dine routes *efter* blueprintet er defineret
#    Så Flask registrerer @admin_bp.route-dekorationerne korrekt
from webapp.admin import routes
