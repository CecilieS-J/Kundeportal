from flask import render_template, request
from webapp.sfcc_service.service import SFCCService
from webapp.sfcc_service import sfcc_service_bp



@sfcc_service_bp.route('/lookup', methods=['GET'])
def lookup_customer():
    query = request.args.get("query")
    result = None

    if query:
        service = SFCCService()
        result = service.fetch_customer_by_customer_no(query.strip())

    return render_template("sfcc_lookup.html", result=result)

# @sfcc_service_bp.route("/lookup", methods=["GET", "POST"])
# def sfcc_lookup():
#     form = SFCCLookupForm()
#     result = None
#
#     if form.validate_on_submit():
#         service = SFCCService()
#         result = service.fetch_customer_data(form.query.data)
#
#     return render_template("lookup.html", form=form, result=result)