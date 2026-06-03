from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from services.mail_service import MailService


class SchedulerService:
    def __init__(self, app) -> None:
        self.app = app
        self.scheduler = BackgroundScheduler(timezone="Europe/Minsk")
        self.job_id = "next_month_birthdays"

    def register_jobs(self) -> None:
        self.scheduler.add_job(
            self._run_next_month_notification,
            CronTrigger(
                day=self.app.config["MONTHLY_NOTIFICATION_DAY"],
                hour=self.app.config["MONTHLY_NOTIFICATION_HOUR"],
                minute=0,
            ),
            id=self.job_id,
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        self.scheduler.add_job(
            self._run_today_notification,
            CronTrigger(
                hour=self.app.config["DAILY_NOTIFICATION_HOUR"],
                minute=0,
            ),
            id="today_birthdays",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

    def start(self) -> None:
        if self.scheduler.running:
            return
        self.register_jobs()
        self.scheduler.start()
        self.app.logger.info("Планировщик уведомлений запущен.")

    def _run_next_month_notification(self) -> None:
        with self.app.app_context():
            try:
                MailService().send_next_month_birthdays()
            except Exception:
                self.app.logger.exception("Ошибка планировщика ежемесячной рассылки.")

    def _run_today_notification(self) -> None:
        with self.app.app_context():
            try:
                MailService().send_today_birthdays()
            except Exception:
                self.app.logger.exception("Ошибка планировщика ежедневной рассылки.")
