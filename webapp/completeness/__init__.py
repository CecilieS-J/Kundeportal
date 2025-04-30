# webapp/completeness/__init__.py

from flask import Blueprint

# 1) Definér blueprint
completeness_bp = Blueprint(
    'completeness',            # endpoints som completeness.missing
    __name__,
    url_prefix='/completeness',
    template_folder='templates/completeness'
)

# 2) Importér routes *efter* blueprintet er defineret
from webapp.completeness import routes
