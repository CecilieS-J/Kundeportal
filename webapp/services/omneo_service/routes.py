from flask import render_template, request
from webapp.services.omneo_service.forms import OmneoLookupForm
from webapp.services.omneo_service.service import OmneoService
from webapp.services.omneo_service import omneo_service_bp

@omneo_service_bp.route("/lookup", methods=["GET", "POST"])
def lookup():
    form = OmneoLookupForm()
    result = None
    error = None

    if form.validate_on_submit():
        service = OmneoService()
        if form.member_id.data:
            result = service.fetch_member_by_id(form.member_id.data)
        elif form.email.data:
            result = service.fetch_member_by_email(form.email.data)
        else:
            error = "Indtast enten et GoodieCard ID eller en e-mailadresse"

        if not result:
            error = "Kunde ikke fundet"

    return render_template("omneo_service/lookup.html", form=form, result=result, error=error)
