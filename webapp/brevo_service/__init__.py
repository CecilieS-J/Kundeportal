from flask import Blueprint

brevo_service_bp = Blueprint(
    "brevo_service",
    __name__,
    url_prefix="/brevo",
    template_folder="templates"  
)

from webapp.brevo_service import routes
