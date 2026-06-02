from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

from forms.employee_forms import EmployeeForm
from services.employee_service import EmployeeService


employee_bp = Blueprint("employees", __name__)


@employee_bp.route("/")
@login_required
def index():
    service = EmployeeService()
    pagination = service.list_paginated(
        page=request.args.get("page", 1, type=int),
        per_page=15,
        full_name=request.args.get("full_name"),
        company_name=request.args.get("company_name"),
        department=request.args.get("department"),
        sort=request.args.get("sort", "full_name"),
        direction=request.args.get("direction", "asc"),
    )
    return render_template(
        "employees/index.html",
        pagination=pagination,
        departments=service.departments(),
    )


@employee_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = EmployeeForm()
    if form.validate_on_submit():
        try:
            EmployeeService().create(_form_data(form))
            current_app.logger.info("Создан сотрудник: %s", form.full_name.data)
            flash("Сотрудник добавлен.", "success")
            return redirect(url_for("employees.index"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("employees/form.html", form=form, title="Добавить сотрудника")


@employee_bp.route("/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
def edit(employee_id: int):
    service = EmployeeService()
    employee = service.get_or_404(employee_id)
    form = EmployeeForm(obj=employee)
    if form.validate_on_submit():
        try:
            service.update(employee_id, _form_data(form))
            current_app.logger.info("Изменен сотрудник: %s", form.full_name.data)
            flash("Сотрудник обновлен.", "success")
            return redirect(url_for("employees.index"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("employees/form.html", form=form, title="Редактировать сотрудника")


@employee_bp.route("/<int:employee_id>/delete", methods=["POST"])
@login_required
def delete(employee_id: int):
    EmployeeService().delete(employee_id)
    current_app.logger.info("Удален сотрудник ID=%s", employee_id)
    flash("Сотрудник удален.", "info")
    return redirect(url_for("employees.index"))


def _form_data(form: EmployeeForm) -> dict:
    return {
        "company_name": form.company_name.data.strip(),
        "full_name": form.full_name.data.strip(),
        "position": form.position.data.strip(),
        "department": form.department.data.strip() if form.department.data else None,
        "birth_date": form.birth_date.data,
        "notes": form.notes.data.strip() if form.notes.data else None,
    }

