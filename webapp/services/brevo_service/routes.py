from flask import request, render_template
from webapp.services.brevo_service.service import BrevoService
from webapp.services.brevo_service import brevo_service_bp

@brevo_service_bp.route('/lookup', methods=['GET'])
def lookup_contact():
    query = request.args.get('query')
    result = None

    if query:
        service = BrevoService()
        result = service.fetch_contact(query)

    return render_template('brevo_service/lookup.html', result=result)
