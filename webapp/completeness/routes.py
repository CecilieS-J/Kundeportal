from webapp.completeness import completeness_bp
from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user
from flask_login import login_required
from webapp import db
from webapp.models import Customer, ExternalSystem, CheckRun, CheckResult, UserRole
from webapp.auth.utils import require_roles



@completeness_bp.route('/missing', methods=['GET', 'POST'])
@login_required
@require_roles(UserRole.dataansvarlig, UserRole.it_supporter)
def missing_customers():
    if request.method == 'POST':
        # Eksempel: læs tekstfelt med kommaseparerede external_id’er
        ids = [e.strip() for e in request.form['external_ids'].split(',') if e.strip()]

        # Opdater Customer-tabellen
        customers = []
        for ext in ids:
            c = Customer.query.filter_by(external_id=ext).first()
            if not c:
                c = Customer(external_id=ext)
                db.session.add(c)
            customers.append(c)
        db.session.commit()

        # Opret et nyt CheckRun og tilhørende CheckResults
        run = CheckRun(run_type='missing', initiated_by=current_user.id)
        db.session.add(run)
        db.session.flush()

        systems = ExternalSystem.query.all()
        for cust in customers:
            for sys in systems:
                res = CheckResult(
                    check_run_id=run.id,
                    customer_id=cust.id,
                    system_id=sys.id,
                    status='missing'
                )
                db.session.add(res)
        db.session.commit()

        flash(f"Tjek færdigt: {len(customers)} kunder mod {len(systems)} systemer", "success")
        return render_template('completeness/results.html', run=run)

    return render_template('completeness/form.html')
