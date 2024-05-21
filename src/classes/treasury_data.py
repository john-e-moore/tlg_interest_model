from dataclasses import dataclass, field
from datetime import date, datetime
import pandas as pd
from typing import List, Union
from treasury_security import Bond, Note, Bill, InflationProtectedSecurity, FloatingRateNote

@dataclass
class TreasuryData:
    securities: List[Union['Bill', 'Note', 'Bond', 'InflationProtectedSecurity', 'FloatingRateNote']] = field(default_factory=list)
    start_date: date = field(default=date.today())
    end_date: date = field(default=date.today())

    def load_data(self, file_path: str):
        df = pd.read_csv(file_path)
        self.securities = self._create_securities_from_df(df)

    def _create_securities_from_df(self, df: pd.DataFrame) -> List:
        securities = []
        for _, row in df.iterrows():
            security_type = row['type']
            common_args = {
                'security_id': row['id'],
                'issue_date': datetime.strptime(row['issue_date'], '%Y-%m-%d').date(),
                'maturity_date': datetime.strptime(row['maturity_date'], '%Y-%m-%d').date(),
                'initial_amount': row['initial_amount'],
                'interest_rate': row['interest_rate'],
            }
            if security_type == 'bill':
                security = Bill(**common_args, discount_rate=row['discount_rate'])
            elif security_type == 'note':
                security = Note(**common_args)
            elif security_type == 'bond':
                security = Bond(**common_args)
            elif security_type == 'tips':
                security = InflationProtectedSecurity(**common_args, inflation_index=row['inflation_index'])
            elif security_type == 'frn':
                security = FloatingRateNote(**common_args, floating_rate_index=row['floating_rate_index'])
            securities.append(security)
        return securities

    # NOTE: don't need method for rolling over; 

    def save_results(self, file_path: str):
        # Convert securities data back to DataFrame and save to CSV
        data = [vars(security) for security in self.securities]
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
