# webapp/auth/routes.py

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta, timezone

from webapp import db
from webapp.models import User
from webapp.auth import auth_bp
from webapp.auth.forms import LoginForm, ChangePasswordForm
from webapp.auth.utils import record_login

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            record_login(user.id, request.remote_addr)
            session.permanent = True

            # ENSARTET tjek af udløb
            expires = user.pw_expires_at  # <— altid defineret (selv om det er None)

            if expires is None:
                must_change = True
            else:
                if expires.tzinfo is None:
                    expires = expires.replace(tzinfo=timezone.utc)
                must_change = expires <= datetime.now(timezone.utc)

            if must_change:
                return redirect(url_for('auth.change_password', next=request.args.get('next')))

            next_page = request.args.get('next') or url_for('public.home')
            return redirect(next_page)

        flash("Forkert brugernavn eller kodeord", "danger")

    return render_template('auth/login.html', form=form, title="Log ind")


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Du er nu logget ud", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Opdater password og udløbstid
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
