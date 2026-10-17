"""Gabarito do exercício 2."""
import datetime as dt

ONE_DAY = dt.timedelta(days=1)


def _is_business_day(day: dt.date, holidays: set[dt.date]) -> bool:
    return day.weekday() < 5 and day not in holidays   # set: O(1)


def next_business_day(day: dt.date, holidays: set[dt.date]) -> dt.date:
    candidate = day + ONE_DAY
    while not _is_business_day(candidate, holidays):
        candidate += ONE_DAY
    return candidate


def add_business_days(day: dt.date, count: int,
                      holidays: set[dt.date]) -> dt.date:
    if count < 0:
        raise ValueError("count must be >= 0")
    for _ in range(count):
        day = next_business_day(day, holidays)
    return day
