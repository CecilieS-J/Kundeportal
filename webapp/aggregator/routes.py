from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from webapp.auth.utils import require_roles
from webapp.models import UserRole

from . import aggregator_bp
from .forms import GoodieForm
from .service import CustomerAggregatorService

@aggregator_bp.route('/missing', methods=['GET', 'POST'])
@login_required
@require_roles(UserRole.dataansvarlig, UserRole.it_supporter)
def missing_customers():
    form = GoodieForm()
    if form.validate_on_submit():
        goodie_id = form.goodie_id.data.strip()
        service   = CustomerAggregatorService()
        external  = service.fetch_external(goodie_id)
        return render_template(
            'aggregator/results.html',
            goodie_id=goodie_id,
            external=external
        )

    # Ved GET eller valideringsfejl
    return render_template('aggregator/form.html', form=form)
