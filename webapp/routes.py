from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user


# Define a blueprint for public routes (pages available after login)
public_bp = Blueprint(
    'public',                  # blueprint-name
    __name__,
    template_folder='templates'
)


@public_bp.route('/home')
@login_required
def home():
    # Render the home page (requires login)
    return render_template('home.html', title="Magasin´s KundePortal – Hjem")



# Du kan tilføje flere use-case-routes her, f.eks. completeness, duplicates, osv.
# Bare husk at dekorere med @login_required

# Fallback for alle andre URLs (valgfrit)
@public_bp.app_errorhandler(404)
def page_not_found(e):
    if not current_user.is_authenticated:
        # Anonyme brugere sendes til login
        return redirect(url_for('auth.login', next=request.path))
    # For indloggede: vis en simpel 404
    return render_template('404.html', title="Side ikke fundet"), 404
