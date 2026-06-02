from __future__ import annotations

from models.entities import NotificationRecipient
from repositories.recipient_repository import RecipientRepository


class RecipientService:
    def __init__(self, repository: RecipientRepository | None = None) -> None:
        self.repository = repository or RecipientRepository()

    def list_paginated(self, **kwargs):
        return self.repository.list_paginated(**kwargs)

    def get_or_404(self, recipient_id: int) -> NotificationRecipient:
        recipient = self.repository.get(recipient_id)
        if recipient is None:
            from flask import abort

            abort(404)
        return recipient

    def create(self, data: dict) -> NotificationRecipient:
        self._ensure_email_unique(data["email"])
        return self.repository.create(NotificationRecipient(**data))

    def update(self, recipient_id: int, data: dict) -> NotificationRecipient:
        recipient = self.get_or_404(recipient_id)
        self._ensure_email_unique(data["email"], exclude_id=recipient_id)
        for key, value in data.items():
            setattr(recipient, key, value)
        self.repository.update()
        return recipient

    def delete(self, recipient_id: int) -> None:
        self.repository.delete(self.get_or_404(recipient_id))

    def toggle(self, recipient_id: int) -> NotificationRecipient:
        recipient = self.get_or_404(recipient_id)
        recipient.is_active = not recipient.is_active
        self.repository.update()
        return recipient

    def active(self) -> list[NotificationRecipient]:
        return self.repository.active()

    def _ensure_email_unique(self, email: str, exclude_id: int | None = None) -> None:
        if self.repository.email_exists(email, exclude_id):
            raise ValueError("Получатель с таким email уже существует.")

