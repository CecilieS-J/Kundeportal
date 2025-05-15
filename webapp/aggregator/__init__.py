from flask import Blueprint

# 1) Definér blueprint
aggregator_bp = Blueprint(
    'aggregator',                 # giver endpoints som aggregator.compare_customer
    __name__,
    url_prefix='/aggregator',     # alle ruter bliver /aggregator/…
    template_folder='templates/aggregator'
)

# 2) Importér routes *efter* blueprintet er defineret
from webapp.aggregator import routes
