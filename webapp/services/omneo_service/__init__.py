from flask import Blueprint

omneo_service_bp = Blueprint(
    'omneo_service',
    __name__,
    url_prefix='/omneo',
    template_folder='templates/omneo_service'
)

from webapp.services.omneo_service import routes  # skal stå til sidst for at undgå cirkulær import
