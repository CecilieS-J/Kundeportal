
from flask import Blueprint

external_customer_service_bp = Blueprint(
    'external_customer',
    __name__,
    url_prefix='/external_customer',
    template_folder='templates'
)

from webapp.external_customer_service import routes  # skal stå til sidst for at undgå cirkulær import
