import datetime as dt
import random
import time

import pytest
from dateutil.relativedelta import relativedelta

D = dt.date


def test_exact_age(load_exercise):
    exact_age = load_exercise("ex01_exact_age").exact_age
    assert exact_age(D(1990, 3, 25), D(2026, 10, 12)) == (36, 6, 17)
    assert exact_age(D(1990, 10, 12), D(2026, 10, 12)) == (36, 0, 0)
    assert exact_age(D(1990, 10, 13), D(2026, 10, 12)) == (35, 11, 29)
    assert exact_age(D(2024, 2, 29), D(2025, 2, 28)) == (1, 0, 0)
    assert exact_age(D(2026, 1, 31), D(2026, 3, 1)) == (0, 1, 1)
    with pytest.raises(ValueError):
        exact_age(D(2026, 1, 2), D(2026, 1, 1))


def test_exact_age_matches_relativedelta(load_exercise):
    exact_age = load_exercise("ex01_exact_age").exact_age
    rng = random.Random(12)
    base = D(1980, 1, 1)
    for _ in range(300):
        born = base + dt.timedelta(days=rng.randrange(0, 15000))
        today = born + dt.timedelta(days=rng.randrange(0, 15000))
        rd = relativedelta(today, born)
        assert exact_age(born, today) == (rd.years, rd.months, rd.days), (
            born, today)


def test_next_business_day(load_exercise):
    mod = load_exercise("ex02_next_business_day")
    assert mod.next_business_day(D(2026, 10, 9), set()) == D(2026, 10, 12)
    assert mod.next_business_day(D(2026, 10, 8), set()) == D(2026, 10, 9)
    assert mod.next_business_day(D(2026, 10, 10), set()) == D(2026, 10, 12)
    holidays = {D(2026, 10, 12)}
    assert mod.next_business_day(D(2026, 10, 9), holidays) == D(2026, 10, 13)
    holidays = {D(2026, 12, 24), D(2026, 12, 25)}
    assert mod.next_business_day(D(2026, 12, 23), holidays) == D(2026, 12, 28)


def test_add_business_days(load_exercise):
    mod = load_exercise("ex02_next_business_day")
    assert mod.add_business_days(D(2026, 10, 10), 0, set()) == D(2026, 10, 10)
    assert mod.add_business_days(D(2026, 10, 9), 5, set()) == D(2026, 10, 16)
    holidays = {D(2026, 10, 12)}
    assert mod.add_business_days(D(2026, 10, 9), 1, holidays) == D(2026, 10, 13)
    with pytest.raises(ValueError):
        mod.add_business_days(D(2026, 10, 9), -1, set())


def test_convert_meeting_basic(load_exercise):
    convert = load_exercise("ex03_convert_meeting").convert_meeting
    r = convert(dt.datetime(2026, 10, 12, 14), "America/Sao_Paulo",
                "Asia/Tokyo")
    assert r.isoformat() == "2026-10-13T02:00:00+09:00"
    # Nova York muda para o horário de verão em 2024-03-10.
    before = convert(dt.datetime(2024, 3, 8, 9), "America/New_York",
                     "America/Sao_Paulo")
    after = convert(dt.datetime(2024, 3, 11, 9), "America/New_York",
                    "America/Sao_Paulo")
    assert before.hour == 11 and after.hour == 10


def test_convert_meeting_dst_edges(load_exercise):
    convert = load_exercise("ex03_convert_meeting").convert_meeting
    sp = "America/Sao_Paulo"
    with pytest.raises(ValueError):          # 00:30 não existiu
        convert(dt.datetime(2018, 11, 4, 0, 30), sp, "UTC")
    first = convert(dt.datetime(2019, 2, 16, 23, 30), sp, "UTC")
    second = convert(dt.datetime(2019, 2, 16, 23, 30), sp, "UTC", fold=1)
    assert (first.day, first.hour, first.minute) == (17, 1, 30)
    assert (second.day, second.hour, second.minute) == (17, 2, 30)
    assert first.utcoffset() == dt.timedelta(0)


def test_convert_meeting_rejects_aware(load_exercise):
    convert = load_exercise("ex03_convert_meeting").convert_meeting
    with pytest.raises(ValueError):
        convert(dt.datetime(2026, 1, 1, tzinfo=dt.UTC), "UTC", "UTC")


def test_add_months(load_exercise):
    add_months = load_exercise("ex04_add_months").add_months
    assert add_months(D(2026, 1, 31), 1) == D(2026, 2, 28)
    assert add_months(D(2024, 1, 31), 1) == D(2024, 2, 29)
    assert add_months(D(2026, 3, 31), -1) == D(2026, 2, 28)
    assert add_months(D(2026, 11, 15), 3) == D(2027, 2, 15)
    assert add_months(D(2026, 1, 15), -13) == D(2024, 12, 15)
    assert add_months(D(2026, 5, 31), 0) == D(2026, 5, 31)
    assert add_months(D(2024, 2, 29), 12) == D(2025, 2, 28)


def test_add_months_matches_relativedelta(load_exercise):
    add_months = load_exercise("ex04_add_months").add_months
    rng = random.Random(7)
    for _ in range(300):
        day = D(2000, 1, 1) + dt.timedelta(days=rng.randrange(9000))
        n = rng.randrange(-60, 60)
        assert add_months(day, n) == day + relativedelta(months=n)


@pytest.mark.parametrize("text", [
    "2026-10-12",                  # sem hora
    "2026-10-12T09:30:00",         # sem fuso
    "2026-10-12 09:30:00Z",        # espaço no lugar do T
    "20261012T093000Z",            # formato básico
    "2026-10-12t09:30:00Z",        # t minúsculo
    "2026-10-12T09:30Z",           # sem segundos
    "2026-02-30T00:00:00Z",        # data impossível
    "2026-10-12T25:00:00Z",        # hora impossível
    "2026-10-12T09:30:00+0300",    # offset sem dois-pontos
    "",
])
def test_strict_rejects(load_exercise, text):
    parse_strict = load_exercise("ex05_strict_iso").parse_strict
    with pytest.raises(ValueError) as info:
        parse_strict(text)
    assert repr(text) in str(info.value)


def test_strict_accepts(load_exercise):
    parse_strict = load_exercise("ex05_strict_iso").parse_strict
    assert parse_strict("2026-10-12T09:30:00Z").isoformat() == (
        "2026-10-12T09:30:00+00:00")
    r = parse_strict("2026-10-12T09:30:00.5-03:00")
    assert r.utcoffset() == dt.timedelta(hours=-3)
    assert r.microsecond == 500000
    assert parse_strict("2026-10-12T09:30:00+05:30").tzinfo is not None


def test_timer(load_exercise):
    Timer = load_exercise("ex06_timer").Timer
    timer = Timer()
    assert timer.elapsed == 0 and timer.elapsed_ns == 0
    with timer as t:
        time.sleep(0.02)
    assert t is timer
    assert isinstance(timer.elapsed_ns, int)
    assert 0.015 <= timer.elapsed < 2
    assert timer.elapsed == pytest.approx(timer.elapsed_ns / 1e9)


def test_timer_does_not_swallow_exceptions(load_exercise):
    Timer = load_exercise("ex06_timer").Timer
    timer = Timer()
    with pytest.raises(KeyError):
        with timer:
            raise KeyError("boom")
    assert timer.elapsed_ns > 0
