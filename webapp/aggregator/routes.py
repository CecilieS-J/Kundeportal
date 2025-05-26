from flask import render_template, request, redirect, url_for, abort
from . import aggregator_bp
from .forms import CustomerLookupForm
from .service import CustomerAggregator

@aggregator_bp.route('/', methods=['GET', 'POST'])
def customer_form():
    form = CustomerLookupForm()
    if form.validate_on_submit():
        # Redirect til details – ingen service-kald her
        param = form.search_type.data   # fx 'email' eller 'sib_id'
        value = form.query.data
        return redirect(url_for('aggregator.customer_details', **{param: value}))
    return render_template('customer_search.html', form=form)

@aggregator_bp.route('/details', methods=['GET'])
def customer_details():
    # Hent søgeparametre fra URL’en
    email       = request.args.get('email')
    customer_no = request.args.get('customer_no')
    goodie_id   = request.args.get('goodie_id')
    sib_id      = request.args.get('sib_id')

    if not any([email, customer_no, goodie_id, sib_id]):
        abort(400, description="Angiv mindst én af: email, customer_no, goodie_id eller sib_id")

    # Kald din aggregator-service her
    aggregator = CustomerAggregator()
    result = aggregator.fetch_customer(
        email=email,
        customer_no=customer_no,
        goodie_id=goodie_id,
        sib_id=sib_id
    )

    # Hvis ingen data, vis med null-værdier og 404-status
    if not result:
        return render_template(
            'customer_details.html',
            external=None,
            sfcc=None,
            events=None
        ), 404

    # Ellers render med data
    return render_template(
        'customer_details.html',
        external=result['external'],
        sfcc=result['sfcc'],
        events=result['events']
    )
