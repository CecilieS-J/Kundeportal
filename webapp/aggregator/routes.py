from flask import (
    render_template, request, redirect, url_for, flash, current_app
)
from . import aggregator_bp
from .forms import CustomerLookupForm
from .service import CustomerAggregator
from flask_login import login_required
from webapp.auth.service import require_roles
from webapp.models import UserRole
import io
import pandas as pd

@aggregator_bp.route('/', methods=['GET', 'POST'])
@login_required
@require_roles(UserRole.admin, UserRole.it_supporter, UserRole.watcher)
def customer_form():
    form = CustomerLookupForm()

    if form.validate_on_submit():
        uploaded = form.file.data
        has_file = uploaded and uploaded.filename.lower().endswith(('.csv', '.xlsx'))
        has_query = bool(form.query.data and form.query.data.strip())

        if has_file and has_query:
            flash('Vælg enten en søgeværdi eller upload en fil – ikke begge.', 'warning')
            return render_template('customer_search.html', form=form)

        if not has_file and not has_query:
            flash('Du skal enten indtaste en søgeværdi eller uploade en fil.', 'warning')
            return render_template('customer_search.html', form=form)

        if has_file:
            # --- BULK-UPLOAD-gren ---
            agg = CustomerAggregator()
            try:
                # Læs data fra fil (CSV eller XLSX)
                if uploaded.filename.lower().endswith('.xlsx'):
                    content = uploaded.read()
                    df = pd.read_excel(io.BytesIO(content), dtype=str, header=0)
                else:
                    text = uploaded.stream.read().decode('utf-8')
                    df = pd.read_csv(io.StringIO(text), dtype=str, header=0)

                # --- Find den korrekte kolonne ud fra form.search_type ---
                df.columns = df.columns.astype(str)
                col_map = {col.lower(): col for col in df.columns}
                key = form.search_type.data

                # Hvis der ikke findes en direkte kolonne, tjek alternativer
                if key in col_map:
                    col = col_map[key]
                else:
                    found = False
                    alt_map = {
                        'goodie_id':   ['goodiecard'],
                        'customer_no': ['customerno', 'customer no'],
                        'email':       ['email']
                    }
                    for alt in alt_map.get(key, []):
                        if alt in col_map:
                            col = col_map[alt]
                            found = True
                            break
                    if not found:
                        if df.empty or df.shape[1] == 0:
                            flash('Filen indeholder ingen kolonner.', 'error')
                            return render_template('customer_search.html', form=form)
                        col = df.columns[0]

                # Ekstraher identifikatorer fra den valgte kolonne
                identifiers = df[col].dropna().astype(str).str.strip().unique()

                # Trim evt. “.0” fra tal, der er blevet læst som floats
                identifiers = [i[:-2] if i.endswith('.0') else i for i in identifiers]
                identifiers = [i for i in identifiers if i]

                if not identifiers:
                    flash('Ingen gyldige rækker fundet i filen.', 'info')
                    return render_template('customer_search.html', form=form)

                # Log kun i denne gren, hvor identifiers er defineret
                current_app.logger.debug(f"Identifiers fundet i filen: {identifiers!r}")
                queries = ','.join(identifiers)
                current_app.logger.debug(f"Samlede queries-streng: {queries!r}")

                return redirect(url_for(
                    'aggregator.bulk_results',
                    queries=queries,
                    search_type=form.search_type.data
                ))

            except Exception as e:
                flash(f'Fejl ved læsning af fil: {e}', 'error')
                return render_template('customer_search.html', form=form)

        # --- ENKELTSØGNING-gren (has_query er True her) ---
        return redirect(url_for(
            'aggregator.customer_details',
            **{form.search_type.data: form.query.data.strip()}
        ))

    return render_template('customer_search.html', form=form)


@aggregator_bp.route('/bulk', methods=['GET'])
@login_required
@require_roles(UserRole.admin, UserRole.it_supporter, UserRole.watcher)
def bulk_results():
    queries = request.args.get('queries', '')
    search_type = request.args.get('search_type')
    if not queries:
        flash('Ingen bulk-resultater at vise.', 'warning')
        return redirect(url_for('aggregator.customer_form'))

    agg = CustomerAggregator()
    results = []
    for q in queries.split(','):
        q = q.strip()
        if not q:
            continue
        data = agg.fetch_customer(**{search_type: q})
        results.append({
            'query': q,
            'external': data.get('external', {}),
            'brevo': data.get('brevo', {}),
            'omneo': data.get('omneo', {}),
            'sfcc': data.get('sfcc', {}),
            'events': data.get('events', [])
        })

    return render_template(
        'bulk.result.html',
        results=results,
        search_type=search_type,
        queries=queries
    )


@aggregator_bp.route('/details', methods=['GET'])
@login_required
@require_roles(UserRole.admin, UserRole.it_supporter, UserRole.watcher)
def customer_details():
    email = request.args.get('email')
    customer_no = request.args.get('customer_no')
    goodie_id = request.args.get('goodie_id')
    sib_id = request.args.get('sib_id')
    bulk_flag = request.args.get('bulk')
    queries = request.args.get('queries')
    search_type = request.args.get('search_type')

    agg = CustomerAggregator()
    result = agg.fetch_customer(
        email=email,
        customer_no=customer_no,
        goodie_id=goodie_id,
        sib_id=sib_id
    )

    # Calculate differences
    diffs = agg.find_differences(
        brevo=result.get('brevo', {}),
        mdm=result.get('mdm', {}),
        omneo=result.get('omneo', {}),
        sfcc=result.get('sfcc', {})
    )

    return render_template(
        'customer_details.html',
        brevo=result.get('brevo', {}),
        mdm=result.get('mdm', {}),
        omneo=result.get('omneo', {}),
        sfcc=result.get('sfcc', {}),
        #events=result.get('events', []),
        diffs=diffs,
        bulk=bulk_flag,
        queries=queries,
        search_type=search_type
    ), (404 if not result else 200)