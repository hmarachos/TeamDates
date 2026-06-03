from __future__ import annotations

import smtplib
from datetime import date, datetime
from email.message import EmailMessage

from flask import current_app, render_template

from models.entities import EmailNotificationLog, NotificationStatus, NotificationType
from repositories.log_repository import EmailLogRepository
from services.employee_service import EmployeeService
from services.recipient_service import RecipientService


MONTH_NAMES = {
    1: "январе",
    2: "феврале",
    3: "марте",
    4: "апреле",
    5: "мае",
    6: "июне",
    7: "июле",
    8: "августе",
    9: "сентябре",
    10: "октябре",
    11: "ноябре",
    12: "декабре",
}


class MailService:
    def __init__(
        self,
        employee_service: EmployeeService | None = None,
        recipient_service: RecipientService | None = None,
        log_repository: EmailLogRepository | None = None,
    ) -> None:
        self.employee_service = employee_service or EmployeeService()
        self.recipient_service = recipient_service or RecipientService()
        self.log_repository = log_repository or EmailLogRepository()

    def _has_sent_notification_today(self, notification_type: NotificationType, reference_date: date | None = None) -> bool:
        """Проверяет, было ли уведомление этого типа отправлено сегодня."""
        today = reference_date or date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        existing = EmailNotificationLog.query.filter(
            EmailNotificationLog.notification_type == notification_type.value,
            EmailNotificationLog.sent_at >= today_start,
            EmailNotificationLog.sent_at <= today_end,
            EmailNotificationLog.status == NotificationStatus.SUCCESS.value
        ).first()
        
        return existing is not None

    def send_next_month_birthdays(self, reference_date: date | None = None) -> int:
        today = reference_date or date.today()
        
        # Проверка на дублирование
        if self._has_sent_notification_today(NotificationType.NEXT_MONTH_BIRTHDAYS, today):
            current_app.logger.info("Уведомление о днях рождения следующего месяца уже было отправлено сегодня.")
            return 0
        
        rows = self.employee_service.next_month_birthdays(today)
        if not rows:
            current_app.logger.info("Нет дней рождения в следующем месяце.")
            return 0

        target_month = today.month + 1 if today.month < 12 else 1
        target_year = today.year if today.month < 12 else today.year + 1
        subject = f"Дни рождения сотрудников в {MONTH_NAMES[target_month]} {target_year} года"
        html = render_template(
            "emails/next_month_birthdays.html",
            rows=rows,
            subject=subject,
            period=f"{MONTH_NAMES[target_month]} {target_year} года",
            generated_at=datetime.now(),
        )
        text = render_template(
            "emails/next_month_birthdays.txt",
            rows=rows,
            subject=subject,
            period=f"{MONTH_NAMES[target_month]} {target_year} года",
            generated_at=datetime.now(),
        )
        return self._send_to_active_recipients(
            subject,
            html,
            text,
            NotificationType.NEXT_MONTH_BIRTHDAYS,
        )

    def send_today_birthdays(self, reference_date: date | None = None) -> int:
        today = reference_date or date.today()
        
        # Проверка на дублирование
        if self._has_sent_notification_today(NotificationType.TODAY_BIRTHDAY, today):
            current_app.logger.info("Уведомление о днях рождения сегодня уже было отправлено сегодня.")
            return 0
        
        rows = self.employee_service.today_birthdays(today)
        if not rows:
            current_app.logger.info("Сегодня нет дней рождения сотрудников.")
            return 0

        subject = (
            "Сегодня день рождения сотрудника"
            if len(rows) == 1
            else "Сегодня день рождения сотрудников"
        )
        html = render_template("emails/today_birthdays.html", rows=rows, subject=subject)
        text = render_template("emails/today_birthdays.txt", rows=rows, subject=subject)
        return self._send_to_active_recipients(
            subject,
            html,
            text,
            NotificationType.TODAY_BIRTHDAY,
        )

    def send_test_email(self, recipient_email: str) -> None:
        subject = "Тестовое письмо системы дней рождения"
        html = render_template("emails/test_email.html", subject=subject)
        text = "Тестовое письмо успешно сформировано системой напоминаний о днях рождения."
        self._send_message(recipient_email, subject, html, text, NotificationType.TEST_EMAIL)

    def _send_to_active_recipients(
        self,
        subject: str,
        html: str,
        text: str,
        notification_type: NotificationType,
    ) -> int:
        recipients = self.recipient_service.active()
        sent = 0
        for recipient in recipients:
            self._send_message(recipient.email, subject, html, text, notification_type)
            sent += 1
        return sent

    def _send_message(
        self,
        recipient_email: str,
        subject: str,
        html: str,
        text: str,
        notification_type: NotificationType,
    ) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = current_app.config["MAIL_FROM"]
        message["To"] = recipient_email
        message.set_content(text)
        message.add_alternative(html, subtype="html")

        try:
            with self._smtp_client() as client:
                username = current_app.config["SMTP_USERNAME"]
                password = current_app.config["SMTP_PASSWORD"]
                if username and password:
                    client.login(username, password)
                client.send_message(message)
            self._log(notification_type, recipient_email, subject, NotificationStatus.SUCCESS)
            current_app.logger.info("Письмо отправлено: %s", recipient_email)
        except Exception as exc:
            self._log(
                notification_type,
                recipient_email,
                subject,
                NotificationStatus.FAILED,
                str(exc),
            )
            current_app.logger.exception("Ошибка SMTP при отправке письма %s", recipient_email)
            raise

    def _smtp_client(self):
        client = smtplib.SMTP(
            current_app.config["SMTP_HOST"],
            current_app.config["SMTP_PORT"],
            timeout=current_app.config["SMTP_TIMEOUT"],
        )
        if current_app.config["SMTP_USE_TLS"]:
            client.starttls()
        return client

    def _log(
        self,
        notification_type: NotificationType,
        recipient_email: str,
        subject: str,
        status: NotificationStatus,
        error_message: str | None = None,
    ) -> None:
        self.log_repository.create(
            EmailNotificationLog(
                notification_type=notification_type.value,
                recipient_email=recipient_email,
                subject=subject,
                status=status.value,
                error_message=error_message,
            )
        )
