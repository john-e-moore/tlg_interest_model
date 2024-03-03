import os
import json
import pandas as pd
import pyarrow
import argparse
from typing import Dict
from utils import load_config
from simulation import calculate_interest_payments, reissue_security

def main(
        config: dict,
        issue_new_debt: bool, 
        use_fiscal_calendar: bool, 
        interest_rates: Dict[int, float]) -> None:
    # Read the .csv containing securities data.
    usecols = [
        'Record Date',
        #'Security Type Description', # Marketable or Non-Marketable
        'Security Class 1 Description', # Type of security
        'Security Class 2 Description', # CUSIP ID number (unique for each security)
        'Interest Rate',
        'Yield',
        'Issue Date',
        'Maturity Date',
        'Issued Amount (in Millions)', # Read as non-numeric due to *
        #'Outstanding Amount (in Millions)', # Read as non-numeric due to *
    ]
    raw_data_path = config['io']['raw_data_path']
    df = pd.read_csv(raw_data_path, usecols=usecols)
    print(df.dtypes)
    print(f"Shape: {df.shape}")

    ################################################################################
    # Preprocessing.
    ################################################################################

    """
    Security types: As of writing, only interested in non-TIPS, non-FSN marketable securities.

    Yes: 'Notes', 'Bonds', 'Bills Maturity Value'
    No: 'Inflation-Protected Securities', 'Floating Rate Notes'
    """
    # Ensure valid security types were passed
    class_1_descriptions_to_keep = config['simulation']['security_types']
    valid_class_1_descriptions = df['Security Class 1 Description'].unique()
    invalid_security_passed = any(x not in valid_class_1_descriptions for x in class_1_descriptions_to_keep)
    if invalid_security_passed:
        raise ValueError("An invalid security type was passed. Ensure all security types are included in raw data.")
    # Filter data
    df = df[df['Security Class 1 Description'].isin(class_1_descriptions_to_keep)]
    print(f"Filtered to specified security types: {class_1_descriptions_to_keep}")
    print(f"Shape: {df.shape}")

    """
    Duplicates: Raw data is append-only, so there can be multiple lines for
    the same security with different record dates. 
    
    Note this is different than adding onto a security, which will have a 
    different issue date, so we drop on both ID and issue date.
    """
    subset = ['Security Class 2 Description', 'Issue Date']
    df.drop_duplicates(subset=subset, keep='first', inplace=True)
    print("Duplicates dropped.")
    print(f"Shape: {df.shape}")

    # Some records represent totals; we only want individual securities.
    # These all contain the string 'Total' in their descriptions.
    df = df[~df['Security Class 2 Description'].str.contains('Total')]
    print("Totals records removed.")
    print(f"Shape: {df.shape}")

    # Change columns to numeric.
    df['Issued Amount (in Millions)'] = pd.to_numeric(df['Issued Amount (in Millions)'])

    # Change columns to datetime after dropping nulls.
    df.dropna(subset=['Issue Date', 'Maturity Date'], inplace=True) # (1)
    df['Issue Date'] = pd.to_datetime(df['Issue Date'])
    df['Maturity Date'] = pd.to_datetime(df['Maturity Date'])
    df['Record Date'] = pd.to_datetime(df['Record Date'])

    # Max record date; don't need to reissue anything that matures before this.
    max_record_date = df['Record Date'].max()
    print(f"Max record date: {max_record_date}")
    df.drop('Record Date', axis=1, inplace=True)

    # Safety: ensures the reissue function doesn't run forever due to error in raw data.
    df['term_days'] = (df['Maturity Date'] - df['Issue Date']).dt.days
    df = df[df['term_days'] > 0]
    print("Negative term records removed.")
    print(f"Shape: {df.shape}")
    
    ################################################################################
    # Simulate reissuance of debts.
    ################################################################################

    # Only reissue debt that expires after max record date. 
    # Any debt issued before it is already captured in the data.
    reissue_df = df[df['Maturity Date'] >= max_record_date].reset_index(drop=True)
    print(f"Number of securities in original data to be reissued: {len(reissue_df)}")
    print("Simulating reissuance...")
    ## Parameters
    reissue_end_date = pd.to_datetime(config['simulation']['reissue_end_date'])
    ## Apply function
    reissue_list = reissue_df.apply(
        func=reissue_security,
        axis=1,
        args=(interest_rates, reissue_end_date,)).tolist()
    print("Complete. Concatenating results...")
    reissue_result = pd.concat(reissue_list, axis=0, ignore_index=True)
    print("Complete.")
    print(f"Number of reissued securities in data: {len(reissue_result)}")

    # Concatenate the new dataframes with the original one.
    df = pd.concat([df, reissue_result], axis=0, ignore_index=True)
    print(f"Number of rows after combining: {len(df)}")

    ################################################################################
    # Simulate new debts.
    ################################################################################

    gdp_millions = config['simulation']['gdp_millions']
    gdp_growth_rate = config['simulation']['gdp_growth_rate']
    new_debt_pct_gdp = config['simulation']['new_debt_pct_gdp']

    ################################################################################
    # Calculate yearly interest payments.
    ################################################################################

    # Add year, month, day columns for interest payment calculation.
    df['year_issued'] = df['Issue Date'].dt.year
    df['month_issued'] = df['Issue Date'].dt.month
    df['day_issued'] = df['Issue Date'].dt.day
    df['year_matured'] = df['Maturity Date'].dt.year
    df['month_matured'] = df['Maturity Date'].dt.month
    df['day_matured'] = df['Maturity Date'].dt.day

    # Calculate interest payments on each security then recombine into time series.
    processed_rows = df.apply(calculate_interest_payments, axis=1)
    df_yearly = pd.DataFrame(processed_rows.tolist())

    # Reorder year columns.
    year_columns = [col for col in df_yearly.columns if col.isdigit() and 1900 <= int(col) <= 2100]
    non_year_columns = [col for col in df_yearly.columns if col not in year_columns]
    sorted_year_columns = sorted(year_columns, key=lambda x: int(x))
    df_yearly_sorted = df_yearly[non_year_columns + sorted_year_columns]
    
    # Sum yearly interest payments by id and security type.
    df_yearly_sorted.drop(['issue_date', 'maturity_date'], axis=1, inplace=True)
    id_grouped_df = df_yearly_sorted.groupby(['id', 'security_type'], as_index=False).sum()

    # Melt and pivot sum of interest payments on year.
    # NOTE: if desired, you can group by both security type and year.
    id_grouped_df.drop('id', axis=1, inplace=True)
    df_melted = id_grouped_df.melt(id_vars=["security_type"], var_name="year", value_name="interest_payment")
    pivot_table = pd.pivot_table(df_melted, values="interest_payment", index=["year"], aggfunc='sum')
    pivot_table['interest_payment'] = pivot_table['interest_payment'].round(2)

    # Save output
    output_path = config['io']['output_path']
    pivot_table.to_csv(output_path)

if __name__ == "__main__":
    """
    Author: John Moore (2024-03-04)

    Objective: Calculate US Gov't debt burden thru 2050.

    Assumptions:
    * All debts get reissued immediately when they mature.

    Simulation config parameters:
    * Interest rates when debt gets created or reissued.
    * Which security types get included in the simulation
      (currently 'Notes', 'Bonds', 'Bills Maturity Value')
    """
    # Load config.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.yml')
    config = load_config(config_path)

    # Default interest rate
    interest_rates_default = config['simulation']['interest_rates_default']

    # Initialize argument parser and add arguments
    parser = argparse.ArgumentParser(description='Process the arguments for debt management.')
    parser.add_argument('--issue-new-debt', action='store_true', help='Flag to issue new debt (default: false)')
    parser.add_argument('--use-fiscal-calendar', action='store_true', help='Flag to use fiscal calendar (default: false)')
    parser.add_argument('--interest-rates', type=json.loads, default=interest_rates_default,
                        help='Dictionary of interest rates with term as key and rate as value (default is 5 percent for all securities)')

    # Parsing arguments
    args = parser.parse_args()

    # Convert interest rates keys from str to int if necessary
    interest_rates_converted = {int(k): v for k, v in args.interest_rates.items()}

    main(config, args.issue_new_debt, args.use_fiscal_calendar, interest_rates_converted)