from flask import render_template
from flask_login import login_required
from webapp.auth.utils import require_roles
from webapp.models import UserRole
from . import aggregator_bp
from .forms import GoodieForm
from .service import CustomerAggregatorService
import io
import pandas as pd

@aggregator_bp.route('/missing', methods=['GET', 'POST'])
@login_required
@require_roles(UserRole.dataansvarlig, UserRole.it_supporter)
def missing_customers():
    form = GoodieForm()
    if not form.validate_on_submit():
        return render_template('aggregator/form.html', form=form)

    service = CustomerAggregatorService()
    stype   = form.search_type.data         # fx 'sib_id' eller 'phone'
    val     = form.query_value.data.strip() or None
    results = []

    # Enkeltsøgning
    if val:
        row = service.aggregate(**{stype: val})
        results.append({'søgeværdi': val, **row})

    # Bulk via Excel – kun hvis fil rent faktisk er uploadet
    file_data = form.excel_file.data
    if file_data and getattr(file_data, 'filename', None):
        # Læs indholdet som bytes
        content = file_data.read()
        df = pd.read_excel(io.BytesIO(content), dtype=str)
        for raw in df.iloc[:, 0].dropna().unique():
            raw_str = str(raw).strip()
            # Fjern evt. ".0" hvis pandas konverterede tal til float
            if raw_str.endswith('.0'):
                raw_str = raw_str[:-2]
            row = service.aggregate(**{stype: raw_str})
            results.append({'søgeværdi': raw_str, **row})

        return render_template('aggregator/results_bulk.html', results=results)

    # Returner enkelt-resultat
    first = results[0] if results else {}
    return render_template(
        'aggregator/results.html',
        goodie_id=first.get('søgeværdi', ''),
        external=first
    )