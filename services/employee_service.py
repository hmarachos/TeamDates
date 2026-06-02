from __future__ import annotations

from datetime import date

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from models.entities import EmployeeBirthday
from repositories.employee_repository import EmployeeRepository
from services.age_calculation_service import AgeCalculationService


class EmployeeService:
    def __init__(self, repository: EmployeeRepository | None = None) -> None:
        self.repository = repository or EmployeeRepository()
        self.age_service = AgeCalculationService()

    def list_paginated(self, **kwargs):
        return self.repository.list_paginated(**kwargs)

    def get_or_404(self, employee_id: int) -> EmployeeBirthday:
        employee = self.repository.get(employee_id)
        if employee is None:
            from flask import abort

            abort(404)
        return employee

    def create(self, data: dict) -> EmployeeBirthday:
        self._ensure_unique(data["company_name"], data["full_name"], data["birth_date"])
        employee = EmployeeBirthday(**data)
        try:
            return self.repository.create(employee)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError(
                "Сотрудник с таким предприятием, ФИО и датой рождения уже существует."
            ) from exc

    def update(self, employee_id: int, data: dict) -> EmployeeBirthday:
        employee = self.get_or_404(employee_id)
        self._ensure_unique(
            data["company_name"],
            data["full_name"],
            data["birth_date"],
            exclude_id=employee_id,
        )
        for key, value in data.items():
            setattr(employee, key, value)
        try:
            self.repository.update()
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError(
                "Сотрудник с таким предприятием, ФИО и датой рождения уже существует."
            ) from exc
        return employee

    def delete(self, employee_id: int) -> None:
        self.repository.delete(self.get_or_404(employee_id))

    def departments(self) -> list[str]:
        return self.repository.departments()

    def upcoming_birthdays(
        self,
        days: int = 30,
        reference_date: date | None = None,
    ) -> list[dict]:
        today = reference_date or date.today()
        items: list[dict] = []
        for employee in self.repository.all():
            days_left = self.age_service.days_until_birthday(employee.birth_date, today)
            if 0 <= days_left <= days:
                items.append(
                    {
                        "employee": employee,
                        "next_birthday": self.age_service.calculate_next_birthday(
                            employee.birth_date,
                            today,
                        ),
                        "next_age": self.age_service.calculate_next_age(
                            employee.birth_date,
                            today,
                        ),
                        "days_left": days_left,
                    }
                )
        return sorted(items, key=lambda row: (row["days_left"], row["employee"].full_name))

    def next_month_birthdays(self, reference_date: date | None = None) -> list[dict]:
        today = reference_date or date.today()
        month = today.month + 1 if today.month < 12 else 1
        year = today.year if today.month < 12 else today.year + 1
        rows = []
        for employee in self.repository.by_month(month):
            birthday = self.age_service.calculate_next_birthday(employee.birth_date, today)
            if birthday.year == year and birthday.month == month:
                rows.append(
                    {
                        "employee": employee,
                        "birthday": birthday,
                        "age": self.age_service.calculate_next_age(employee.birth_date, today),
                    }
                )
        return rows

    def today_birthdays(self, reference_date: date | None = None) -> list[dict]:
        today = reference_date or date.today()
        rows = []
        for employee in self.repository.by_month_day(today.month, today.day):
            rows.append(
                {
                    "employee": employee,
                    "birthday": today,
                    "age": today.year - employee.birth_date.year,
                }
            )
        return rows

    def _ensure_unique(
        self,
        company_name: str,
        full_name: str,
        birth_date: date,
        exclude_id: int | None = None,
    ) -> None:
        if self.repository.exists_duplicate(company_name, full_name, birth_date, exclude_id):
            raise ValueError("Сотрудник с таким предприятием, ФИО и датой рождения уже существует.")
