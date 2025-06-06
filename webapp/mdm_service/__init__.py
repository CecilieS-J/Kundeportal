
from flask import Blueprint

mdm_service_bp = Blueprint(
    'mdm_service',
    __name__,
    url_prefix='/mdm_service',
    template_folder='templates'
)

from webapp.mdm_service import routes  # skal stå til sidst for at undgå cirkulær import
