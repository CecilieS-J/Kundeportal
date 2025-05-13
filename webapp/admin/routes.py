# webapp/admin/routes.py
import os
from webapp.admin import admin_bp
from flask import render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash
from flask_login import login_required
from datetime import datetime, timezone
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
        default_pw = "Magasin2025"
        now = datetime.now(timezone.utc)

        u = User(
            username=form.username.data,
            email=form.email.data, 
            password_hash=generate_password_hash(default_pw),
            role=UserRole[form.role.data],
            pw_changed_at=now,
            pw_expires_at=now
        )
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.username.errors.append('Brugernavn optaget')
        else:
            # Send velkomst-mail
            subject = "Din bruger er oprettet"
            body = (
                f"Kære {u.username},\n\n"
                "Din bruger i Kundeportalen er nu oprettet.\n"
                f"Brugernavn: {u.username}\n"
                f"Adgangskode er blevet udleveret\n\n"
                "Når du logger ind første gang, vil du blive bedt om at ændre din adgangskode.\n\n"
                "Venlig hilsen\n"
                "IT-support"
            )
            try:
                send_alert(subject, [u.email], body)
                flash(f"Bruger oprettet og mail sendt til {u.email}", "success")
            except Exception:
                flash("Bruger oprettet, men fejl ved afsendelse af velkomst-mail", "warning")

            return redirect(url_for('admin.list_users'))

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