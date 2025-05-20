from flask import Blueprint

sfcc_service_bp = Blueprint(
    "sfcc_service",
    __name__,
    url_prefix="/sfcc",
    template_folder="templates/sfcc_service"
)

from webapp.services.sfcc_service import routes  # Importér routes EFTER blueprint
