from flask import render_template
from flask_login import login_required
from webapp.auth.service import require_roles
from webapp.models import UserRole
from . import mdm_service_bp
from .forms import GoodieForm, EventForm
from .service import MdmService
import io
import pandas as pd

@mdm_service_bp.route('/search', methods=['GET', 'POST'])
@login_required
@require_roles(UserRole.admin, UserRole.it_supporter)
def search_customers_mdm():
    """
    Allows data responsible and IT support users to search for customer data in MDM.
    Supports single lookups and bulk search via Excel file upload.
    """
    form = GoodieForm()
    if not form.validate_on_submit():
        return render_template('form.html', form=form)

    service =   MdmService()
    stype   = form.search_type.data         # e.g., 'sib_id' or 'phone'
    val     = form.query_value.data.strip() or None
    results = []

    # Single search query
    if val:
        row = service.fetch_mdm_customer(**{stype: val})
        results.append({'søgeværdi': val, **row})

    # Bulk search via uploaded Excel file (if provided)
    file_data = form.excel_file.data
    if file_data and getattr(file_data, 'filename', None):
        # Read uploaded file as bytes
        content = file_data.read()
        df = pd.read_excel(io.BytesIO(content), dtype=str)
        for raw in df.iloc[:, 0].dropna().unique():
            raw_str = str(raw).strip()
             # Remove trailing ".0" if pandas interpreted number as float
            if raw_str.endswith('.0'):
                raw_str = raw_str[:-2]
            row = service.fetch_mdm_customer(**{stype: raw_str})
            results.append({'søgeværdi': raw_str, **row})

        return render_template('results_bulk.html', results=results)

    # Return single search result
    first = results[0] if results else {}
    return render_template(
        'results.html',
        goodie_id=first.get('søgeværdi', ''),
        mdm=first
    )


@mdm_service_bp.route('/events', methods=['GET', 'POST'])
@login_required
@require_roles(UserRole.admin, UserRole.it_supporter)
def event_log():
    """
    Displays the event log for a given customer based on goodie ID.
    Access is restricted to users with the 'admin' or 'it_supporter' role.
    """

    # Initialize the form used to input the goodie ID
    form = EventForm()
    events = []  # Will store the event log results

    # If the form is submitted and passes validation
    if form.validate_on_submit():
        # Read and clean the goodie ID from the form input
        gid = form.goodie_id.data.strip()

        # Create an instance of the mdm service integration
        service = MdmService()

        # Call the service method to fetch events for the given goodie ID
        events = service.fetch_event_log(goodie_id=gid)

    # Render the event log page with form and results (if any)
    return render_template(
        'event_log.html',
        form=form,
        events=events
    )


