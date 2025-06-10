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





# Fallback for others # routes that are not defined
@public_bp.app_errorhandler(404)
def page_not_found(e):
    if not current_user.is_authenticated:
        # Anonymes users sends to login
        # Redirect to login page with the original path as next parameter
        # This allows the user to be redirected back after login
        return redirect(url_for('auth.login', next=request.path))
    # If user is authenticated, show a custom 404 page
    return render_template('404.html', title="Side ikke fundet"), 404
