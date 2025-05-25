# webapp/comparison/routes.py
import logging
from flask import (
    request, jsonify, render_template, flash, current_app
)
from comparison.comparer import compare_customer_data
from comparison import comparison_bp

# Sæt en logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@comparison_bp.route("/", methods=["GET"])
def compare():
    identifier      = request.args.get("identifier", "").strip()
    identifier_type = request.args.get("identifier_type", "email")
    fmt             = request.args.get("format", "html")

    logger.debug(f"👉 compare called with identifier={identifier!r}, type={identifier_type!r}, format={fmt!r}")

    if fmt == "html":
        # 1) Hvis brugeren klikker "Søg" uden at indtaste noget:
        if not identifier:
            flash("Du skal indtaste e-mail, kundenummer eller Goodiecard.", "warning")
            return render_template("compare.html", data=None, chart_config=None)

        # 2) Ellers prøv at hente data
        try:
            result = compare_customer_data(identifier, identifier_type)
            chart_config = {
                "type": "bar",
                "data": {
                    "labels": ["Systemer med data", "Felter med forskelle"],
                    "datasets": [{
                        "label": "Synkroniseringsstatus",
                        "data": [
                            4 - len(result.get("not_found", [])),
                            len(result.get("differences", {}))
                        ],
                        "backgroundColor": ["#28a745", "#ffc107"],
                        "borderColor":     ["#218838", "#e0a800"],
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "scales": {
                        "y": {"beginAtZero": True, "title": {"display": True, "text": "Antal"}},
                        "x": {"title": {"display": True, "text": "Kategori"}}
                    },
                    "plugins": {
                        "legend": {"display": False},
                        "title": {
                            "display": True,
                            "text": f"Synkroniseringsoversigt for {result.get('identifier', 'ukendt')}"
                        }
                    }
                }
            }
            return render_template("compare.html",
                                   data=result,
                                   chart_config=chart_config,
                                   error=None)
        except Exception as e:
            current_app.logger.exception("Fejl i compare_customer_data")
            flash(f"Der opstod en fejl: {e}", "danger")
            return render_template("compare.html",
                                   data=None,
                                   chart_config=None,
                                   error=str(e))

    # JSON-API fallback
    if not identifier:
        return jsonify({"error": "Missing identifier parameter"}), 400

    try:
        result = compare_customer_data(identifier, identifier_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
