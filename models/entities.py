from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from flask_login import UserMixin
from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class NotificationType(StrEnum):
    NEXT_MONTH_BIRTHDAYS = "NEXT_MONTH_BIRTHDAYS"
    TODAY_BIRTHDAY = "TODAY_BIRTHDAY"
    TEST_EMAIL = "TEST_EMAIL"


class NotificationStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class EmployeeBirthday(db.Model, TimestampMixin):
    __tablename__ = "employee_birthdays"
    __table_args__ = (
        UniqueConstraint(
            "company_name",
            "full_name",
            "birth_date",
            name="uq_employee_company_fullname_birthdate",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<EmployeeBirthday {self.full_name}>"


class NotificationRecipient(db.Model, TimestampMixin):
    __tablename__ = "notification_recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<NotificationRecipient {self.email}>"


class EmailNotificationLog(db.Model):
    __tablename__ = "email_notification_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

