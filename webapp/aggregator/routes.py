from flask import Blueprint, request, jsonify, render_template
from webapp.aggregator.service import CustomerAggregatorService

aggregator_bp = Blueprint('aggregator', __name__)

@aggregator_bp.route('/compare_customer', methods=['GET'])
def compare_customer():
    goodie_id = request.args.get('goodie_id')

    profile = None
    if goodie_id:
        aggregator = CustomerAggregatorService()
        profile = aggregator.compare_customer_profile(goodie_id=goodie_id)

    return render_template('aggregator/compare.html', profile=profile)