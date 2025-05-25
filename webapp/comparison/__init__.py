from flask import Blueprint

comparison_bp = Blueprint(
    "comparison",
    __name__,
    url_prefix="/compare",
    template_folder="templates"
)

from comparison import routes
