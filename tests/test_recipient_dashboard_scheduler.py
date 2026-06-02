from datetime import date

from models.entities import NotificationRecipient
from repositories.log_repository import EmailLogRepository
from repositories.recipient_repository import RecipientRepository
from services.dashboard_service import DashboardService
from services.employee_service import EmployeeService
from services.recipient_service import RecipientService
from services.scheduler_service import SchedulerService


def test_recipient_service_crud_and_toggle(app_ctx):
    service = RecipientService()
    recipient = service.create(
        {"name": "HR", "email": "hr@example.com", "is_active": True}
    )

    updated = service.update(
        recipient.id,
        {"name": "HR Team", "email": "hr-team@example.com", "is_active": True},
    )
    toggled = service.toggle(updated.id)

    assert toggled.is_active is False
    assert RecipientRepository().count_active() == 0

    service.delete(toggled.id)
    assert RecipientRepository().active() == []


def test_recipient_duplicate_email_is_rejected(app_ctx):
    service = RecipientService()
    data = {"name": "HR", "email": "hr@example.com", "is_active": True}

    service.create(data)

    try:
        service.create(data)
    except ValueError as exc:
        assert "уже существует" in str(exc)
    else:
        raise AssertionError("Дубликат email должен быть отклонен.")


def test_dashboard_summary(app_ctx):
    EmployeeService().create(
        {
            "company_name": "Компания",
            "full_name": "Иванов Иван",
            "position": "Инженер",
            "department": "ИТ",
            "birth_date": date.today(),
            "notes": None,
        }
    )
    RecipientRepository().create(
        NotificationRecipient(name="HR", email="hr@example.com", is_active=True)
    )

    summary = DashboardService().summary()

    assert summary["employees_count"] == 1
    assert summary["companies_count"] == 1
    assert summary["active_recipients_count"] == 1
    assert summary["upcoming_count"] == 1


def test_log_repository_latest(app_ctx):
    assert EmailLogRepository().latest() == []


def test_scheduler_registers_jobs(app):
    scheduler = SchedulerService(app)

    scheduler.register_jobs()

    job_ids = {job.id for job in scheduler.scheduler.get_jobs()}
    assert job_ids == {"next_month_birthdays", "today_birthdays"}
