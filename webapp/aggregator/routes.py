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
    # Hent email, customer_no, goodie_id, sib_id fra query params
    email = request.args.get('email')
    customer_no = request.args.get('customer_no')
    goodie_id = request.args.get('goodie_id')
    sib_id = request.args.get('sib_id')

    aggregator = CustomerAggregator()
    result = aggregator.fetch_customer(
        email=email,
        customer_no=customer_no,
        goodie_id=goodie_id,
        sib_id=sib_id
    )

    # Pak værdier ud
    brevo     = result.get('brevo', {})
    external  = result.get('external', {})
    sfcc      = result.get('sfcc', {})
    events    = result.get('events', [])

    # Render med brevo også
    return render_template(
        'customer_details.html',
        brevo=brevo,
        external=external,
        sfcc=sfcc,
        events=events
    ), (404 if not result else 200)
