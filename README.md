# US Government Interest Expense Simulator
## Overview
The purpose of this project is to simulate the US Government's public debt burden in years to come given a set of assumptions. It accounts for debts maturing and being reissued at different interest rates.

![Excel chart made with output](/images/output_chart.png "Excel chart made with output")

## Getting Started
### Prerequisites
A Python installation, and a .csv download of the [U.S. Treasury's Monthly Statement of the Public Debt](https://fiscaldata.treasury.gov/datasets/monthly-statement-public-debt/summary-of-treasury-securities-outstanding).

### Installation
##### Clone repository
`git clone https://github.com/john-e-moore/tlg_wagetracker.git`
##### Create and activate virtual environment
1. `cd tlg_wagetracker`
2. `python -m venv venv`
3. `source venv/bin/activate`
##### Install dependencies
`pip install -r requirements.txt`
##### Configure file locations and simulation parameters
- Change config-example.yml to config.yml. 
- Input values for raw_data_path (the location of the MSPD data you downloaded) and output_path.
- Set simulation parameters.
  - reissue_end_date: The end date for the simulation.
  - security_types: A list of security types to be included in the simulation, such as 'Notes', 'Bonds', 'Bills Maturity Value'. These must match values in the 'Security Class 1 Description' column in the raw data.
  - interest_rates_default: A dictionary with the format {term: interest rate}. If one-year bonds pay out 4% yearly and two-year bonds pay 4.5%, the dictionary would be {1: 4, 2: 4.5}
  - gdp_millions: Estimate of US yearly GDP in millions at the max record date in the dataset. If you pulled the data at the start of 2024, just look up the 2023 GDP and use that number (in millions).
  - gdp_growth_rate: Estimate of average GDP growth rate over the term of the simulation.
  - new_debt_pct_gdp: Estimate of the deficit as a percentage of GDP over the term of the simulation.
  - new_debt_interest_rate: Estimate of the average Fed Funds rate over the term of the simulation.

## Usage
Run main.py and pass desired parameters.
```
python src/main.py \
  --new-debt \
  --interest-rates '{"1": 4.99, "2": 4.6, "3": 4.3, "5": 4.2, "7": 4.1, "10": 4.1, "20": 4.3, "30": 4.2}' \
  --gdp-millions 27944627 \
  --gdp-growth-rate 6.0 \
  --new-debt-pct-gdp 6.3 \
  --new-debt-interest-rate 5.0
```

Output will be written to the output folder specified in config.