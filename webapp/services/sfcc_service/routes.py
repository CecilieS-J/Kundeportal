from flask import render_template, request
from webapp.services.sfcc_service.forms import SFCCLookupForm
from webapp.services.sfcc_service.service import SFCCService
from webapp.services.sfcc_service import sfcc_service_bp



@sfcc_service_bp.route('/sfcc/lookup', methods=['GET', 'POST'])
def lookup_customer():
    form = SFCCLookupForm()
    result = None

    if form.validate_on_submit():
        customer_no = form.customer_no.data
        service = SFCCService()
        result = service.fetch_customer_data(customer_no)

    return render_template('sfcc_service/lookup.html', form=form, result=result)

# @sfcc_service_bp.route("/lookup", methods=["GET", "POST"])
# def sfcc_lookup():
#     form = SFCCLookupForm()
#     result = None
#
#     if form.validate_on_submit():
#         service = SFCCService()
#         result = service.fetch_customer_data(form.query.data)
#
#     return render_template("sfcc_service/lookup.html", form=form, result=result)