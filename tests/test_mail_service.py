from datetime import date

from models.entities import NotificationRecipient
from repositories.recipient_repository import RecipientRepository
from services.employee_service import EmployeeService
from services.mail_service import MailService


class DummySMTP:
    sent_messages = []

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def starttls(self):
        return None

    def login(self, username, password):
        return None

    def send_message(self, message):
        self.sent_messages.append(message)


def test_send_today_birthdays(app_ctx, monkeypatch):
    DummySMTP.sent_messages = []
    monkeypatch.setattr("services.mail_service.smtplib.SMTP", DummySMTP)
    EmployeeService().create(
        {
            "company_name": "Компания",
            "full_name": "Иванов Иван",
            "position": "Инженер",
            "department": None,
            "birth_date": date(1985, 6, 2),
            "notes": None,
        }
    )
    RecipientRepository().create(
        NotificationRecipient(name="HR", email="hr@example.com", is_active=True)
    )

    sent = MailService().send_today_birthdays(reference_date=date(2026, 6, 2))

    assert sent == 1
    assert DummySMTP.sent_messages[0]["To"] == "hr@example.com"


def test_send_next_month_birthdays(app_ctx, monkeypatch):
    DummySMTP.sent_messages = []
    monkeypatch.setattr("services.mail_service.smtplib.SMTP", DummySMTP)
    EmployeeService().create(
        {
            "company_name": "Компания",
            "full_name": "Петров Петр",
            "position": "Специалист",
            "department": None,
            "birth_date": date(1990, 7, 15),
            "notes": None,
        }
    )
    RecipientRepository().create(
        NotificationRecipient(name="HR", email="hr@example.com", is_active=True)
    )

    sent = MailService().send_next_month_birthdays(reference_date=date(2026, 6, 25))

    assert sent == 1
    assert "июле 2026" in DummySMTP.sent_messages[0]["Subject"]
