from datetime import date

from services.age_calculation_service import AgeCalculationService


def test_calculate_next_age_for_future_birthday():
    service = AgeCalculationService()

    age = service.calculate_next_age(date(1985, 7, 15), date(2026, 6, 20))

    assert age == 41


def test_days_until_birthday_rolls_to_next_year():
    service = AgeCalculationService()

    days = service.days_until_birthday(date(1990, 1, 10), date(2026, 1, 11))

    assert days == 364


def test_leap_day_uses_february_28_in_common_year():
    service = AgeCalculationService()

    birthday = service.calculate_next_birthday(date(2000, 2, 29), date(2026, 2, 1))

    assert birthday == date(2026, 2, 28)

