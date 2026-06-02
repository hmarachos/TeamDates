from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from forms.auth_forms import LoginForm
from repositories.user_repository import UserRepository


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = UserRepository().find_by_username(form.username.data.strip())
        if user and user.is_active and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            current_app.logger.info("Вход в систему: %s", user.username)
            return redirect(request.args.get("next") or url_for("dashboard.index"))
        flash("Неверный логин или пароль.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    current_app.logger.info("Выход из системы: %s", current_user.username)
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth.login"))

