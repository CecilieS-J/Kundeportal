from flask import Blueprint

sfcc_service_bp = Blueprint(
    "sfcc_service",
    __name__,
    url_prefix="/sfcc",
    template_folder="templates"  
)

from webapp.sfcc_service import routes
