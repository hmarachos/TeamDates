from __future__ import annotations

from repositories.employee_repository import EmployeeRepository
from repositories.recipient_repository import RecipientRepository
from services.employee_service import EmployeeService


class DashboardService:
    def __init__(self) -> None:
        self.employee_repository = EmployeeRepository()
        self.recipient_repository = RecipientRepository()
        self.employee_service = EmployeeService(self.employee_repository)

    def summary(self) -> dict:
        upcoming = self.employee_service.upcoming_birthdays(days=30)
        return {
            "employees_count": self.employee_repository.count(),
            "companies_count": self.employee_repository.count_companies(),
            "active_recipients_count": self.recipient_repository.count_active(),
            "upcoming_count": len(upcoming),
            "upcoming_birthdays": upcoming,
        }

