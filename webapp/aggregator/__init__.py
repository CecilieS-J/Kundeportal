# webapp/aggregator/__init__.py
from flask import Blueprint

aggregator_bp = Blueprint(
    'aggregator',
    __name__,
    url_prefix='/aggregator',
    template_folder='templates/aggregator'
)

from webapp.aggregator import routes