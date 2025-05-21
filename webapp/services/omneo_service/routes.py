from flask import render_template
from webapp.services.omneo_service.forms import OmneoLookupForm
from webapp.services.omneo_service.service import OmneoService
from webapp.services.omneo_service import omneo_service_bp

@omneo_service_bp.route("/lookup", methods=["GET", "POST"])
def lookup():
    form = OmneoLookupForm()
    service = OmneoService()
    results = []
    error = None
    search_mode = False  # Til at styre visning af top 10 eller søgeresultater

    if form.validate_on_submit():
        query_value = form.query_value.data.strip()
        search_type = form.search_type.data
        search_mode = True  # Vi har forsøgt at søge

        if search_type == 'email':
            results = service.fetch_by_email(query_value)
        elif search_type == 'card_pos':
            results = service.fetch_by_card_pos(query_value)
        else:
            error = "Ugyldig søgetype."

        if not results:
            error = "Ingen kunde fundet."
    else:
        # Kun hent top-profiler hvis det er en GET-request (første load)
        results = service.fetch_top_profiles(limit=10)

    return render_template(
        "omneo_service/lookup.html",
        form=form,
        results=results,
        error=error,
        search_mode=search_mode
    )




@omneo_service_bp.route("/lookup/profile/<profile_id>")
def profile_detail(profile_id):
    service = OmneoService()
    profile = service.fetch_profile_by_id(profile_id)
    if not profile:
        return render_template("omneo_service/error.html", message="Kundeprofil ikke fundet")
    return render_template("omneo_service/profile_detail.html", profile=profile)
