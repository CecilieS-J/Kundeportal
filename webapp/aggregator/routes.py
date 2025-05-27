from flask import (
    render_template, request, redirect, url_for, flash, current_app
)
from . import aggregator_bp
from .forms import CustomerLookupForm
from .service import CustomerAggregator
import io
import pandas as pd

@aggregator_bp.route('/', methods=['GET', 'POST'])
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
            # Bulk-upload → parse, gem queries og redirect til GET-route
            agg = CustomerAggregator()
            try:
                # Læs data fra fil (CSV eller XLSX)
                if uploaded.filename.lower().endswith('.xlsx'):
                    content = uploaded.read()
                    df = pd.read_excel(io.BytesIO(content), dtype=str, header=0)
                else:
                    text = uploaded.stream.read().decode('utf-8')
                    df = pd.read_csv(io.StringIO(text), dtype=str, header=0)

                # Lav mapping fra lowercase til original kolonnenavn
                df.columns = df.columns.astype(str)
                col_map = {col.lower(): col for col in df.columns}
                key = form.search_type.data
                # Alternativ mapping af søgetype til kolonnenavne
                alt_map = {
                    'goodie_id': ['goodiecard'],
                    'customer_no': ['customerno', 'customer no'],
                    'email': ['email']
                }
                # Vælg kolonne: direkte match eller alternativt
                if key in col_map:
                    col = col_map[key]
                else:
                    found = False
                    for alt in alt_map.get(key, []):
                        if alt in col_map:
                            col = col_map[alt]
                            found = True
                            break
                    if not found:
                        # Fallback til første kolonne hvis ingen match
                        if df.empty or df.shape[1] == 0:
                            flash('Filen indeholder ingen kolonner.', 'error')
                            return render_template('customer_search.html', form=form)
                        col = df.columns[0]
                identifiers = df[col].dropna().astype(str).str.strip().unique()
                df.columns = df.columns.astype(str)
                col_map = {col.lower(): col for col in df.columns}
                key = form.search_type.data
                if key in col_map:
                    col = col_map[key]
                    identifiers = df[col].dropna().astype(str).str.strip().unique()
                else:
                    if df.empty or df.shape[1] == 0:
                        flash('Filen indeholder ingen kolonner.', 'error')
                        return render_template('customer_search.html', form=form)
                    identifiers = df.iloc[:, 0].dropna().astype(str).str.strip().unique()

                # Trim “.0” fra værdier
                identifiers = [i[:-2] if i.endswith('.0') else i for i in identifiers]
                identifiers = [i for i in identifiers if i]

                if not identifiers:
                    flash('Ingen gyldige rækker fundet i filen.', 'info')
                    return render_template('customer_search.html', form=form)

                queries = ','.join(identifiers)
                return redirect(url_for(
                    'aggregator.bulk_results',
                    queries=queries,
                    search_type=form.search_type.data
                ))
            except Exception as e:
                flash(f'Fejl ved læsning af fil: {e}', 'error')
                return render_template('customer_search.html', form=form)

        current_app.logger.debug(f"Identifiers fundet i filen: {identifiers!r}")
        queries = ','.join(identifiers)
        current_app.logger.debug(f"Samlede queries-streng: {queries!r}")
         


        # Enkeltsøgning → redirect til details
        return redirect(url_for(
            'aggregator.customer_details',
            **{form.search_type.data: form.query.data.strip()}
        ))

    return render_template('customer_search.html', form=form)


@aggregator_bp.route('/bulk', methods=['GET'])
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

    return render_template(
        'customer_details.html',
        brevo=result.get('brevo', {}),
        external=result.get('external', {}),
        omneo=result.get('omneo', {}),
        sfcc=result.get('sfcc', {}),
        events=result.get('events', []),
        bulk=bulk_flag,
        queries=queries,
        search_type=search_type
    ), (404 if not result else 200)
