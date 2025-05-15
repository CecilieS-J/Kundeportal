from flask import Blueprint

brevo_service_bp = Blueprint(
    'brevo_service',
    __name__,
    url_prefix='/brevo',
    template_folder='templates/brevo_service'
)

# Importér routes EFTER blueprint er defineret
from webapp.services.brevo_service import routes
