from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

from forms.recipient_forms import RecipientForm, TestEmailForm
from services.mail_service import MailService
from services.recipient_service import RecipientService


recipient_bp = Blueprint("recipients", __name__)


@recipient_bp.route("/")
@login_required
def index():
    pagination = RecipientService().list_paginated(
        page=request.args.get("page", 1, type=int),
        per_page=15,
        search=request.args.get("search"),
        sort=request.args.get("sort", "name"),
        direction=request.args.get("direction", "asc"),
    )
    return render_template(
        "recipients/index.html",
        pagination=pagination,
        test_form=TestEmailForm(),
    )


@recipient_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = RecipientForm(is_active=True)
    if form.validate_on_submit():
        try:
            RecipientService().create(_form_data(form))
            current_app.logger.info("Создан получатель: %s", form.email.data)
            flash("Получатель добавлен.", "success")
            return redirect(url_for("recipients.index"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("recipients/form.html", form=form, title="Добавить получателя")


@recipient_bp.route("/<int:recipient_id>/edit", methods=["GET", "POST"])
@login_required
def edit(recipient_id: int):
    service = RecipientService()
    recipient = service.get_or_404(recipient_id)
    form = RecipientForm(obj=recipient)
    if form.validate_on_submit():
        try:
            service.update(recipient_id, _form_data(form))
            current_app.logger.info("Изменен получатель: %s", form.email.data)
            flash("Получатель обновлен.", "success")
            return redirect(url_for("recipients.index"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("recipients/form.html", form=form, title="Редактировать получателя")


@recipient_bp.route("/<int:recipient_id>/delete", methods=["POST"])
@login_required
def delete(recipient_id: int):
    RecipientService().delete(recipient_id)
    current_app.logger.info("Удален получатель ID=%s", recipient_id)
    flash("Получатель удален.", "info")
    return redirect(url_for("recipients.index"))


@recipient_bp.route("/<int:recipient_id>/toggle", methods=["POST"])
@login_required
def toggle(recipient_id: int):
    recipient = RecipientService().toggle(recipient_id)
    state = "включена" if recipient.is_active else "отключена"
    current_app.logger.info("Рассылка %s для %s", state, recipient.email)
    flash(f"Рассылка {state}.", "success")
    return redirect(url_for("recipients.index"))


@recipient_bp.route("/test-email", methods=["POST"])
@login_required
def test_email():
    form = TestEmailForm()
    if form.validate_on_submit():
        try:
            MailService().send_test_email(form.email.data.strip().lower())
            flash("Тестовое письмо отправлено.", "success")
        except Exception as exc:
            flash(f"Ошибка отправки: {exc}", "danger")
    else:
        flash("Проверьте email для тестовой отправки.", "danger")
    return redirect(url_for("recipients.index"))


def _form_data(form: RecipientForm) -> dict:
    return {
        "name": form.name.data.strip(),
        "email": form.email.data.strip().lower(),
        "is_active": bool(form.is_active.data),
    }

