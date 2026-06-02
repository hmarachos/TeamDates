from __future__ import annotations

from datetime import date


class AgeCalculationService:
    def calculate_next_birthday(
        self,
        birth_date: date,
        reference_date: date | None = None,
    ) -> date:
        today = reference_date or date.today()
        birthday = self._safe_birthday(today.year, birth_date)
        if birthday < today:
            birthday = self._safe_birthday(today.year + 1, birth_date)
        return birthday

    def calculate_next_age(
        self,
        birth_date: date,
        reference_date: date | None = None,
    ) -> int:
        next_birthday = self.calculate_next_birthday(birth_date, reference_date)
        return next_birthday.year - birth_date.year

    def days_until_birthday(
        self,
        birth_date: date,
        reference_date: date | None = None,
    ) -> int:
        today = reference_date or date.today()
        return (self.calculate_next_birthday(birth_date, today) - today).days

    def _safe_birthday(self, year: int, birth_date: date) -> date:
        if birth_date.month == 2 and birth_date.day == 29:
            try:
                return date(year, 2, 29)
            except ValueError:
                return date(year, 2, 28)
        return date(year, birth_date.month, birth_date.day)

