from __future__ import annotations

from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required

from forms.employee_forms import ImportForm
from services.excel_service import ExcelService


excel_bp = Blueprint("excel", __name__)


@excel_bp.route("/import", methods=["GET", "POST"])
@login_required
def import_employees():
    form = ImportForm()
    result = None
    if form.validate_on_submit():
        try:
            result = ExcelService().import_employees(form.file.data)
            current_app.logger.info("Импорт Excel: %s", result)
            flash(
                f"Импортировано: {result['imported']}. Пропущено: {result['skipped']}.",
                "success",
            )
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("employees/import.html", form=form, result=result)


@excel_bp.route("/export")
@login_required
def export_employees():
    stream = ExcelService().export_employees()
    filename = f"employee_birthdays_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    current_app.logger.info("Экспорт Excel: %s", filename)
    return send_file(
        stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

