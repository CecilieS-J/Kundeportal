from flask import request, render_template
from flask_login import login_required
from webapp.auth.service import require_roles
from webapp.models import UserRole
from webapp.brevo_service.service import BrevoService
from webapp.brevo_service import brevo_service_bp

@brevo_service_bp.route('/lookup', methods=['GET'])
@login_required
@require_roles(UserRole.admin, UserRole.it_supporter, UserRole.watcher)
def lookup_contact():
    query = request.args.get("query")
    result = None

    if query:
        service = BrevoService()
        result = service.fetch_contact(query.strip())

    return render_template("brevo_lookup.html", result=result)
