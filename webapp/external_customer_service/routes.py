from flask import render_template
from flask_login import login_required
from webapp.auth.utils import require_roles
from webapp.models import UserRole
from . import external_customer_service_bp
from .forms import GoodieForm
from .forms import EventForm 
from .service import CustomerExternalService
import io
import pandas as pd

@external_customer_service_bp.route('/search', methods=['GET', 'POST'])
@login_required
@require_roles(UserRole.dataansvarlig, UserRole.it_supporter)
def search_customers_mdm():
    """
    Allows data responsible and IT support users to search for customer data in MDM.
    Supports single lookups and bulk search via Excel file upload.
    """
    form = GoodieForm()
    if not form.validate_on_submit():
        return render_template('external_customer_service/form.html', form=form)

    service =   CustomerExternalService()
    stype   = form.search_type.data         # e.g., 'sib_id' or 'phone'
    val     = form.query_value.data.strip() or None
    results = []

    # Single search query
    if val:
        row = service.fetch_external_customer(**{stype: val})
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
            row = service.fetch_external_customer(**{stype: raw_str})
            results.append({'søgeværdi': raw_str, **row})

        return render_template('external_customer_service/results_bulk.html', results=results)

    # Return single search result
    first = results[0] if results else {}
    return render_template(
        'external_customer_service/results.html',
        goodie_id=first.get('søgeværdi', ''),
        external=first
    )


@external_customer_service_bp.route('/events', methods=['GET', 'POST'])
@login_required
@require_roles(UserRole.dataansvarlig, UserRole.it_supporter)
def event_log():
    """
    Displays the event log for a given customer based on goodie ID.
    """
    form = EventForm()
    events = []

    if form.validate_on_submit():
        gid = form.goodie_id.data.strip()

        # Opret instans af CustomerExternalService
        service = CustomerExternalService()

        # Kald fetch_event_log via instansen
        events = service.fetch_event_log(goodie_id=gid)

    return render_template(
        'external_customer_service/event_log.html',
        form=form,
        events=events
    )

