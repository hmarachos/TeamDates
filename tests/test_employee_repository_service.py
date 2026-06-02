from datetime import date

from models.entities import EmployeeBirthday
from repositories.employee_repository import EmployeeRepository
from services.employee_service import EmployeeService


def test_repository_search_and_counts(app_ctx):
    repository = EmployeeRepository()
    repository.create(
        EmployeeBirthday(
            company_name="РУП Белоруснефть",
            full_name="Иванов Иван Иванович",
            position="Инженер",
            department="ИТ",
            birth_date=date(1985, 7, 15),
        )
    )

    assert repository.count() == 1
    assert repository.count_companies() == 1
    assert repository.departments() == ["ИТ"]
    assert repository.search_text("Иванов")[0].full_name == "Иванов Иван Иванович"


def test_upcoming_birthdays(app_ctx):
    service = EmployeeService()
    service.create(
        {
            "company_name": "Компания",
            "full_name": "Петров Петр",
            "position": "Специалист",
            "department": None,
            "birth_date": date(1990, 7, 1),
            "notes": None,
        }
    )

    rows = service.upcoming_birthdays(days=30, reference_date=date(2026, 6, 20))

    assert len(rows) == 1
    assert rows[0]["next_age"] == 36


def test_duplicate_employee_is_rejected(app_ctx):
    service = EmployeeService()
    data = {
        "company_name": "Компания",
        "full_name": "Сидоров Сидор",
        "position": "Инженер",
        "department": None,
        "birth_date": date(1991, 8, 2),
        "notes": None,
    }

    service.create(data)

    try:
        service.create(data)
    except ValueError as exc:
        assert "уже существует" in str(exc)
    else:
        raise AssertionError("Дубликат сотрудника должен быть отклонен.")

