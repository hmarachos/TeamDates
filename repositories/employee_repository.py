from __future__ import annotations

from datetime import date

from sqlalchemy import extract, func, or_

from app.extensions import db
from models.entities import EmployeeBirthday


class EmployeeRepository:
    def list_paginated(
        self,
        page: int,
        per_page: int,
        full_name: str | None = None,
        company_name: str | None = None,
        department: str | None = None,
        sort: str = "full_name",
        direction: str = "asc",
    ):
        query = EmployeeBirthday.query
        if full_name:
            query = query.filter(EmployeeBirthday.full_name.ilike(f"%{full_name}%"))
        if company_name:
            query = query.filter(EmployeeBirthday.company_name.ilike(f"%{company_name}%"))
        if department:
            query = query.filter(EmployeeBirthday.department.ilike(f"%{department}%"))

        sort_columns = {
            "company_name": EmployeeBirthday.company_name,
            "full_name": EmployeeBirthday.full_name,
            "position": EmployeeBirthday.position,
            "department": EmployeeBirthday.department,
            "birth_date": EmployeeBirthday.birth_date,
            "created_at": EmployeeBirthday.created_at,
        }
        column = sort_columns.get(sort, EmployeeBirthday.full_name)
        query = query.order_by(column.desc() if direction == "desc" else column.asc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get(self, employee_id: int) -> EmployeeBirthday | None:
        return db.session.get(EmployeeBirthday, employee_id)

    def create(self, employee: EmployeeBirthday) -> EmployeeBirthday:
        db.session.add(employee)
        db.session.commit()
        return employee

    def update(self) -> None:
        db.session.commit()

    def delete(self, employee: EmployeeBirthday) -> None:
        db.session.delete(employee)
        db.session.commit()

    def exists_duplicate(
        self,
        company_name: str,
        full_name: str,
        birth_date: date,
        exclude_id: int | None = None,
    ) -> bool:
        query = EmployeeBirthday.query.filter(
            func.lower(EmployeeBirthday.company_name) == company_name.lower(),
            func.lower(EmployeeBirthday.full_name) == full_name.lower(),
            EmployeeBirthday.birth_date == birth_date,
        )
        if exclude_id:
            query = query.filter(EmployeeBirthday.id != exclude_id)
        return db.session.query(query.exists()).scalar()

    def count(self) -> int:
        return EmployeeBirthday.query.count()

    def count_companies(self) -> int:
        return db.session.query(func.count(func.distinct(EmployeeBirthday.company_name))).scalar() or 0

    def departments(self) -> list[str]:
        rows = (
            db.session.query(EmployeeBirthday.department)
            .filter(EmployeeBirthday.department.isnot(None))
            .filter(EmployeeBirthday.department != "")
            .distinct()
            .order_by(EmployeeBirthday.department.asc())
            .all()
        )
        return [row[0] for row in rows]

    def all(self) -> list[EmployeeBirthday]:
        return EmployeeBirthday.query.order_by(
            EmployeeBirthday.company_name.asc(),
            EmployeeBirthday.full_name.asc(),
        ).all()

    def by_month(self, month: int) -> list[EmployeeBirthday]:
        return (
            EmployeeBirthday.query.filter(extract("month", EmployeeBirthday.birth_date) == month)
            .order_by(
                extract("day", EmployeeBirthday.birth_date).asc(),
                EmployeeBirthday.full_name.asc(),
            )
            .all()
        )

    def by_month_day(self, month: int, day: int) -> list[EmployeeBirthday]:
        return (
            EmployeeBirthday.query.filter(
                extract("month", EmployeeBirthday.birth_date) == month,
                extract("day", EmployeeBirthday.birth_date) == day,
            )
            .order_by(EmployeeBirthday.full_name.asc())
            .all()
        )

    def search_text(self, term: str) -> list[EmployeeBirthday]:
        return EmployeeBirthday.query.filter(
            or_(
                EmployeeBirthday.full_name.ilike(f"%{term}%"),
                EmployeeBirthday.company_name.ilike(f"%{term}%"),
                EmployeeBirthday.position.ilike(f"%{term}%"),
            )
        ).all()

