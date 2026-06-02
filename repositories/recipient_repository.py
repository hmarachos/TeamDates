from __future__ import annotations

from app.extensions import db
from models.entities import NotificationRecipient


class RecipientRepository:
    def list_paginated(
        self,
        page: int,
        per_page: int,
        search: str | None = None,
        sort: str = "name",
        direction: str = "asc",
    ):
        query = NotificationRecipient.query
        if search:
            query = query.filter(
                NotificationRecipient.name.ilike(f"%{search}%")
                | NotificationRecipient.email.ilike(f"%{search}%")
            )
        sort_columns = {
            "name": NotificationRecipient.name,
            "email": NotificationRecipient.email,
            "is_active": NotificationRecipient.is_active,
            "created_at": NotificationRecipient.created_at,
        }
        column = sort_columns.get(sort, NotificationRecipient.name)
        query = query.order_by(column.desc() if direction == "desc" else column.asc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get(self, recipient_id: int) -> NotificationRecipient | None:
        return db.session.get(NotificationRecipient, recipient_id)

    def create(self, recipient: NotificationRecipient) -> NotificationRecipient:
        db.session.add(recipient)
        db.session.commit()
        return recipient

    def update(self) -> None:
        db.session.commit()

    def delete(self, recipient: NotificationRecipient) -> None:
        db.session.delete(recipient)
        db.session.commit()

    def active(self) -> list[NotificationRecipient]:
        return NotificationRecipient.query.filter_by(is_active=True).order_by(
            NotificationRecipient.email.asc()
        ).all()

    def count_active(self) -> int:
        return NotificationRecipient.query.filter_by(is_active=True).count()

    def email_exists(self, email: str, exclude_id: int | None = None) -> bool:
        query = NotificationRecipient.query.filter(
            NotificationRecipient.email.ilike(email.lower())
        )
        if exclude_id:
            query = query.filter(NotificationRecipient.id != exclude_id)
        return db.session.query(query.exists()).scalar()

