# webapp/services/external_customer_service/__init__.py
from flask import Blueprint

external_customer_service_bp = Blueprint(
    'external_customer',
    __name__,
    url_prefix='/external_customer',
    template_folder='templates/external_customer_service'
)

