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
        # Trim og brug None hvis tomt
        goodie_id   = form.goodie_id.data.strip()   or None
        email       = form.email.data.strip()       or None
        customer_no = form.customer_no.data.strip() or None

        service  = CustomerAggregatorService()
        external = service.aggregate(
            goodie_id=goodie_id,
            email=email,
            customer_no=customer_no
        )

        # Hvad skal stå i overskriften?
        søgeværdi = goodie_id or email or customer_no or ''

        return render_template(
            'aggregator/results.html',
            goodie_id=søgeværdi,
            external=external
        )

    # GET eller valideringsfejl → vis form igen
    return render_template('aggregator/form.html', form=form)