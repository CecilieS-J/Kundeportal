# webapp/auth/routes.py

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone
from .forms import LoginForm, ChangePasswordForm, OTPForm



from webapp import db
from webapp.models import User
from webapp.auth import auth_bp
from webapp.auth.utils import handle_login, verify_otp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already authenticated, redirect to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))

    # Load the login form (username + password fields)
    form = LoginForm()

    # When the form is submitted and passes validation
    if form.validate_on_submit():
        # Try to authenticate the user and send a one-time password (OTP)
        user = handle_login(form.username.data, form.password.data)
        if user:
            # Save the user's ID in the session to track OTP verification
            session['otp_user_id'] = user.id
            session.permanent = True  # Use Flask's permanent session settings

            # Inform the user that an OTP has been sent via SMS
            flash("An SMS code has been sent to your phone. Please enter it to log in.", "info")
            print("Redirecting to OTP verification route")  # Debug message

            # Redirect to the second step of the login process (OTP verification)
            return redirect(url_for('auth.verify_otp_route'))
        else:
            # Show a generic error message to prevent username enumeration
            flash("Incorrect username or password", "danger")

    # Render the login page with the form
    return render_template('login.html', form=form, title="Log in")



@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_route():
    user_id = session.get('otp_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    form = OTPForm()
    if form.validate_on_submit():
        user = verify_otp(user_id, form.otp.data)
        if user:
            login_user(user)
            session.pop('otp_user_id', None)
            return redirect(url_for('public.home'))  # eller dashboard etc.

        flash("Ugyldig eller udløbet kode", "danger")

    return render_template("otp_form.html", form=form, title="Bekræft SMS-kode")


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  
    return render_template('logged_out.html', title="Logget ud")


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Allows the user to change their password.
    Updates password hash, change timestamp, and sets a new expiration.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        
        current_user.password_hash = generate_password_hash(form.password.data)
        current_user.pw_changed_at = datetime.now(timezone.utc)
        current_user.pw_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        db.session.commit()
        flash("Adgangskode ændret!", "success")

        next_page = request.args.get('next') or url_for('public.home')
        return redirect(next_page)

    return render_template(
        'change_password.html',
        form=form,
        title="Skift adgangskode"
    )


@auth_bp.route('/activate/<token>', methods=['GET', 'POST'])
def activate(token):
    # 1) Find brugeren på token
    user = User.query.filter_by(secret_token=token).first_or_404()

    # 2) Sammenlign expires på en ensartet måde
    now = datetime.now(timezone.utc)              # <- altid aware UTC
    expires = user.secret_token_expires_at
    if expires is None:
        flash("Ugyldigt aktiveringslink.", "danger")
        return redirect(url_for('auth.login'))

    # Hvis expires er naive, gør den aware
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if now > expires:
        flash("Aktiveringslinket er udløbet.", "danger")
        return redirect(url_for('auth.login'))

    # 3) Håndter form til at sætte password
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Sæt password, datoer og ryd token-felter
        user.password_hash = generate_password_hash(form.password.data)
        user.pw_changed_at = now
        user.pw_expires_at = now + timedelta(days=7)
        user.secret_token = None
        user.secret_token_expires_at = None
        db.session.commit()

        flash("Konto aktiveret! Du kan nu logge ind.", "success")
        return redirect(url_for('auth.login'))

    return render_template('activate.html', form=form, title="Aktivér konto")