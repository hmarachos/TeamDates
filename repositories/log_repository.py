from __future__ import annotations

from app.extensions import db
from models.entities import EmailNotificationLog


class EmailLogRepository:
    def create(self, log: EmailNotificationLog) -> EmailNotificationLog:
        db.session.add(log)
        db.session.commit()
        return log

    def latest(self, limit: int = 50) -> list[EmailNotificationLog]:
        return EmailNotificationLog.query.order_by(
            EmailNotificationLog.sent_at.desc()
        ).limit(limit).all()

