# webapp/admin/routes.py
from secrets import token_urlsafe
import os
from webapp.admin import admin_bp
from flask import render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash
from flask_login import login_required
from datetime import datetime, timezone, timedelta
from webapp import db
from webapp.models import User, UserRole, LoginHistory
from webapp.auth.utils import require_roles
from .forms import CreateUserForm, EditUserForm
from webapp.mail import send_alert
import logging
from sqlalchemy.exc import IntegrityError

admin_mail_logger = logging.getLogger('admin-mail')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
admin_mail_logger.addHandler(handler)
admin_mail_logger.setLevel(logging.DEBUG)


@admin_bp.route('/users', methods=['GET'])
@login_required
@require_roles(UserRole.admin)
def list_users():
    q = request.args.get('q','')
    users = User.query.filter(User.username.contains(q)).all() if q else User.query.all()
    return render_template('admin/users.html', users=users, q=q)

@admin_bp.route('/users/create', methods=['GET','POST'])
@login_required
@require_roles(UserRole.admin)
def create_user():
    form = CreateUserForm()

    if form.validate_on_submit():
        # 1) Generer token + udløbstid (24 timer)
        token = token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=24)

        # 2) Opret bruger UDEN password i databasen
        u = User(
            username=form.username.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            password_hash=None,
            role=UserRole[form.role.data],
            pw_changed_at=None,
            pw_expires_at=None,
            secret_token=token,
            secret_token_expires_at=expires
        )
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            # Tjek om det er e-mail eller username der konflikerer
            msg = str(exc.orig).lower()
            if 'email' in msg:
                form.email.errors.append('E-mail optaget')
            else:
                form.username.errors.append('Brugernavn optaget')
        else:
            # 3) Byg aktiveringslink
            activation_link = url_for('auth.activate', token=token, _external=True)

            # 4) Send mail via Mailgun
            subject = "Aktivér din konto i Kundeportalen"
            body = (
                f"Kære {u.username},\n\n"
                f"Dit brugernavn er: {u.username}\n\n"
                "Din bruger er oprettet og skal nu aktiveres.\n\n"
                f"Klik på dette link for at vælge et kodeord og aktivere kontoen:\n"
                f"{activation_link}\n\n"
                "Linket udløber om 24 timer.\n\n"
                "Venlig hilsen\n"
                "IT-support"
            )
            try:
                send_alert(subject, [u.email], body)
                flash(f"Bruger oprettet – aktiveringslink sendt til {u.email}", "success")
            except Exception:
                flash("Bruger oprettet, men kunne ikke sende aktiveringsmail.", "warning")

            return redirect(url_for('admin.list_users'))

    else:
        # Debug: vis præcist hvilke valideringsfejl der er
        admin_mail_logger.debug("[admin:create_user] validate_on_submit() returnerede False")
        admin_mail_logger.debug(f"[admin:create_user] form.errors = {form.errors!r}")

    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET','POST'])
@login_required
@require_roles(UserRole.admin)
def edit_user(user_id):
    u = User.query.get_or_404(user_id)

    # 1) Instantiér formular med objektet
    form = EditUserForm(obj=u)
    form.username.render_kw = {'readonly': True}

    # 2) Præ-vælg den rigtige rolle (strengen, ikke enum)
    form.role.data = u.role.name    # eller u.role.value, afhængigt af dine choices

    # 3) Håndter POST
    if form.validate_on_submit():
        # Opdater enum ud fra den valgte string
        u.role = UserRole[form.role.data]
        u.phone_number = form.phone_number.data

        # Hvis admin indtaster nyt password, så håndter det
        if form.password.data:
            from werkzeug.security import generate_password_hash
            from datetime import datetime, timedelta, timezone

            u.password_hash = generate_password_hash(form.password.data)
            now = datetime.now(timezone.utc)
            u.pw_changed_at = now
            u.pw_expires_at = now + timedelta(days=7)

        db.session.commit()
        flash("Bruger opdateret", "success")
        return redirect(url_for('admin.list_users'))

    # 4) Render GET eller POST med validerings-errors
    return render_template('admin/edit_user.html', form=form, user=u)


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@require_roles(UserRole.admin)
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    flash("Bruger slettet", "info")
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/login-history')
@login_required
@require_roles(UserRole.admin)
def login_history():
    entries = LoginHistory.query.order_by(LoginHistory.timestamp.desc()).limit(100).all()
    return render_template('admin/login_history.html', entries=entries)


@admin_bp.route('/admin/cleanup-logs')
@login_required
@require_roles(UserRole.admin)
def cleanup_logs():

    log_path = os.path.join('logs', 'cleanup.log')
    try:
        with open(log_path, 'r') as f:
            logs = f.read()
    except FileNotFoundError:
        logs = "Ingen logfil fundet."

    return render_template('admin/cleanup_logs.html', logs=logs)