from flask import Blueprint

# Omdøb til noget konsistent, fx 'aggregator_bp'
aggregator_bp = Blueprint(
    "aggregator",
    __name__,
    url_prefix="/aggregator",
    template_folder="templates"
)

# Når du importerer routes, vil @aggregator_bp.route blive registreret
from . import routes
