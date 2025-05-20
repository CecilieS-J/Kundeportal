# webapp/auth/routes.py

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta, timezone
from .forms import LoginForm, ChangePasswordForm, OTPForm



from webapp import db
from webapp.models import User
from webapp.auth import auth_bp
from webapp.auth.utils import record_login, handle_login, verify_otp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))

    form = LoginForm()
    if form.validate_on_submit():
        # Prøv at validere bruger + kodeord og sende OTP
        user = handle_login(form.username.data, form.password.data)
        if user:
            # Gem bruger-id til OTP-verificering
            session['otp_user_id'] = user.id
            session.permanent = True

            flash("Der er nu sendt en SMS-kode til dit nummer. Indtast den for at logge ind.", "info")
            print("Omdirigerer til verify_otp_route")  #  debug
            return redirect(url_for('auth.verify_otp_route'))
        else:
            flash("Forkert brugernavn eller kodeord", "danger")

    return render_template('auth/login.html', form=form, title="Log ind")


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

    return render_template("auth/otp_form.html", form=form, title="Bekræft SMS-kode")


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # valgfrit, men godt for at rydde alt
    return render_template('auth/logged_out.html', title="Logget ud")


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
        'auth/change_password.html',
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

    return render_template('auth/activate.html', form=form, title="Aktivér konto")