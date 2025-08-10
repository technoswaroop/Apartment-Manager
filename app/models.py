from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Flat:
    id: int
    code: str
    owner_name: str


@dataclass
class Settings:
    monthly_fee: int
    start_year: int
    start_month: int  # 1-12


@dataclass
class Payment:
    id: int
    flat_id: int
    amount: int
    paid_on: date
    period_year: int
    period_month: int
    note: str


@dataclass
class Expense:
    id: int
    category: str  # "Repairs" or "Other"
    amount: int
    spent_on: date
    description: str
    paid_by_flat_id: Optional[int]  # if not None, this is owner-paid (credit to that flat)