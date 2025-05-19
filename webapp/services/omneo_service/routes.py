from flask import request, render_template
from webapp.services.omneo_service import omneo_service_bp
from webapp.services.omneo_service.service import OmneoService

@omneo_service_bp.route('/lookup', methods=['GET'])
def lookup_customer():
    query = request.args.get('query')
    result = None

    if query:
        service = OmneoService()
        result = service.fetch_customer(query)

    return render_template('omneo_service/lookup.html', result=result)
