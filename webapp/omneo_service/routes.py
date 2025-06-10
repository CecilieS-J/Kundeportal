from flask import render_template, redirect, url_for, request
from webapp.omneo_service.forms import OmneoLookupForm
from webapp.omneo_service.service import OmneoService
from webapp.omneo_service import omneo_service_bp
from flask_login import login_required
from webapp.auth.service import require_roles
from webapp.models import UserRole

@omneo_service_bp.route("/lookup", methods=["GET", "POST"])
@login_required
@require_roles(UserRole.admin, UserRole.it_supporter, UserRole.watcher)
def lookup_customer():
    form = OmneoLookupForm()
    service = OmneoService()
    results = []
    error = None
    search_mode = False

    if request.method == "POST" and form.validate_on_submit():
        query_value = form.query_value.data.strip()
        search_type = form.search_type.data
        search_mode = True

        try:
            if search_type == "email":
                results = service.fetch_by_email(query_value)
            elif search_type == "card_pos":
                results = service.fetch_by_card_pos(query_value)
            else:
                error = "Ugyldig søgetype."
                search_mode = False

            if results:
                if len(results) == 1:
                    return redirect(url_for("omneo_service.profile_detail", profile_id=results[0]["id"]))
                else:
                    error = f"Fandt {len(results)} profiler. Forventede én."
            else:
                error = "Ingen kunde fundet for den angivne værdi."
        except Exception as e:
            error = f"Fejl under søgning: {str(e)}"
            search_mode = False

    elif request.method == "GET":
        try:
            results = service.fetch_top_profiles(limit=10)
        except Exception as e:
            error = f"Fejl ved hentning af profiler: {str(e)}"

    return render_template(
        "omneo_lookup.html",
        form=form,
        results=results,
        error=error,
        search_mode=search_mode
    )

@omneo_service_bp.route("/lookup/profile/<profile_id>")
@login_required
@require_roles(UserRole.admin, UserRole.it_supporter, UserRole.watcher)
def profile_detail(profile_id):
    service = OmneoService()
    profile = service.fetch_profile_by_id(profile_id)
    if not profile:
        return render_template("error.html", message="Kundeprofil ikke fundet")
    return render_template("profile_detail.html", profile=profile)
