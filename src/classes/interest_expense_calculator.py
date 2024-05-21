import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from treasury_data import TreasuryData
from plotter import Plotter

@dataclass
class InterestExpenseCalculator:
    treasury_data: TreasuryData
    interest_expenses: dict = field(default_factory=dict)

    def simulate_year(self, year: int) -> float:
        total_expense = sum(security.calculate_interest_expense(year) for security in self.treasury_data.securities)
        self.interest_expenses[year] = total_expense
        return total_expense

    def run_simulation(self):
        for year in range(self.treasury_data.start_date.year, self.treasury_data.end_date.year + 1):
            self.simulate_year(year)

    def save_results(self, file_path: str):
        results_df = pd.DataFrame(list(self.interest_expenses.items()), columns=['Year', 'Interest Expense'])
        results_df.to_csv(file_path, index=False)

    def plot_results(self):
        plotter = Plotter(pd.DataFrame(list(self.interest_expenses.items())), '')
        
