from __future__ import annotations

from datetime import date
from typing import Iterator, Tuple


def format_inr(amount_paise_or_rupees: int) -> str:
    # amount is rupees integer; format with Indian grouping
    amount = int(amount_paise_or_rupees)
    sign = '-' if amount < 0 else ''
    s = str(abs(amount))
    if len(s) <= 3:
        return f"{sign}₹{s}"
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return f"{sign}₹{','.join(parts)},{last3}"


def iterate_periods_inclusive(start_year: int, start_month: int, end_year: int, end_month: int) -> Iterator[Tuple[int, int]]:
    y, m = start_year, start_month
    while (y < end_year) or (y == end_year and m <= end_month):
        yield (y, m)
        m += 1
        if m == 13:
            m = 1
            y += 1


def period_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"