from __future__ import annotations

from models.entities import User


class UserRepository:
    def find_by_username(self, username: str) -> User | None:
        return User.query.filter_by(username=username).first()
