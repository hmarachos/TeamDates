from __future__ import annotations

from flask import Blueprint, render_template


error_bp = Blueprint("errors", __name__)


@error_bp.app_errorhandler(404)
def not_found(error):
    return render_template("errors/error.html", code=404, message="Страница не найдена."), 404


@error_bp.app_errorhandler(500)
def server_error(error):
    return render_template("errors/error.html", code=500, message="Внутренняя ошибка сервера."), 500
