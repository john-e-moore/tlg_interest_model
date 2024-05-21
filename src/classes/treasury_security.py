from dataclasses import dataclass, field
from datetime import date

@dataclass
class TreasurySecurity:
    security_id: str
    issue_date: date
    maturity_date: date
    initial_amount: float
    interest_rate: float

    def calculate_interest_expense(self, year: int) -> float:
        if self.issue_date.year <= year <= self.maturity_date.year:
            return self.initial_amount * self.interest_rate
        return 0.0

    def roll_over(self, new_issue_date: date, new_maturity_date: date):
        self.issue_date = new_issue_date
        self.maturity_date = new_maturity_date

@dataclass
class Bill(TreasurySecurity):
    discount_rate: float = 0.0

    def calculate_interest_expense(self, year: int) -> float:
        if self.issue_date.year <= year <= self.maturity_date.year:
            return self.initial_amount * self.discount_rate
        return 0.0

@dataclass
class Note(TreasurySecurity):
    pass

@dataclass
class Bond(TreasurySecurity):
    pass

@dataclass
class InflationProtectedSecurity(TreasurySecurity):
    inflation_index: float = 1.0

    def calculate_interest_expense(self, year: int) -> float:
        if self.issue_date.year <= year <= self.maturity_date.year:
            adjusted_amount = self.initial_amount * self.inflation_index
            return adjusted_amount * self.interest_rate
        return 0.0

@dataclass
class FloatingRateNote(TreasurySecurity):
    floating_rate_index: float = 0.0

    def calculate_interest_expense(self, year: int) -> float:
        if self.issue_date.year <= year <= self.maturity_date.year:
            return self.initial_amount * self.floating_rate_index
        return 0.0
