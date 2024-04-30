import os
import sys
import json
import pandas as pd
import pyarrow
import argparse
from typing import Dict
from utils import load_config
from simulation import calculate_interest_payments, reissue_security, issue_new_debt, compute_future_gdps

def main(
        raw_data_path: str,
        historical_gdps_path: str,
        output_path: str,
        reissue_end_date: pd.Timestamp,
        new_debt: bool, 
        security_types: list,
        fiscal_calendar: bool, 
        interest_rates: Dict[int, float],
        gdp_millions: int,
        gdp_growth_rate: float,
        new_debt_pct_gdp: float,
        new_debt_interest_rate: float,
        multiplier: float
) -> None:
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
    df = pd.read_csv(raw_data_path, usecols=usecols)
    print(df.dtypes)
    print(f"Shape: {df.shape}")

    ################################################################################
    # Preprocessing.
    ################################################################################

    # TODO: add fiscal calendar capability

    """
    Security types: As of writing, only interested in non-TIPS, non-FSN marketable securities.

    Yes: 'Notes', 'Bonds', 'Bills Maturity Value'
    No: 'Inflation-Protected Securities', 'Floating Rate Notes'
    """
    # Ensure valid security types were passed
    class_1_descriptions_to_keep = security_types
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

    # Simulate new debt if argument was passed.
    if new_debt:
        print(f"Issuing new debt with parameters:")
        print(f"GDP in millions: {gdp_millions}")
        print(f"GDP growth rate: {gdp_growth_rate}")
        print(f"Yearly debt to issue as a percentage of GDP: {new_debt_pct_gdp}")
        print(f"Interest rate for new debt: {new_debt_interest_rate}")
        new_debt_payments = issue_new_debt(
            gdp_millions=gdp_millions, 
            gdp_growth_rate=gdp_growth_rate, 
            new_debt_pct_gdp=new_debt_pct_gdp, 
            interest_rate=new_debt_interest_rate,
            start_date=max_record_date, 
            end_date=reissue_end_date
        )
        print(f"New debt payments: {new_debt_payments}")
        # Add new debts to id_grouped_df
        new_row = {col: new_debt_payments.get(col, 0) for col in id_grouped_df.columns}
        new_row['id'] = 'Simulated new debt payments'
        new_row['security_type'] = 'All'
        id_grouped_df.loc[len(id_grouped_df)] = new_row
        print("Tail:")
        print(id_grouped_df[['id', 'security_type', '2024', '2025', '2026']].tail())
        id_grouped_df.to_csv('id_grouped.csv')

    # Load historical GDPs
    historical_gdps = pd.read_csv(historical_gdps_path, index_col='year')
    historical_gdps.index = historical_gdps.index.astype(str)
    print(f"Historical gpds:\n{historical_gdps.head()}")
    # Compute end of year GDPs by year
    future_gdps = compute_future_gdps(
        gdp_millions=gdp_millions, 
        gdp_growth_rate=gdp_growth_rate, 
        start_date=max_record_date, 
        end_date=reissue_end_date
    )
    future_gdps_df = pd.DataFrame.from_dict(
        future_gdps, 
        orient='index',
        columns=['gdp_millions_end_of_year'])
    future_gdps_df.index = future_gdps_df.index.astype(str)
    gdps_df = pd.concat([historical_gdps, future_gdps_df], axis=0)
    gdps_df['gdp_millions_end_of_year'] = gdps_df['gdp_millions_end_of_year'].astype(int)
    gdps_df.to_csv('gdps.csv')

    # Melt and pivot sum of interest payments on year.
    # NOTE: if desired, you can group by both security type and year.
    print("Tail:")
    print(id_grouped_df[['id', 'security_type', '2024', '2025', '2026']].tail())
    id_grouped_df.drop('id', axis=1, inplace=True)
    df_melted = id_grouped_df.melt(id_vars=["security_type"], var_name="year", value_name="interest_payment")
    pivot_table = pd.pivot_table(df_melted, values="interest_payment", index=["year"], aggfunc='sum')
    # Apply multiplier
    # NOTE: this accounts for Bills, Bonds, and Notes only making up
    # about 84% of the public debt. Functionality for TIPS etc. not implemented
    # yet.
    pivot_table['interest_payment'] = pivot_table['interest_payment'] * multiplier
    pivot_table['interest_payment'] = pivot_table['interest_payment'].round(2)
    pivot_table.to_csv('pivot_table_initial.csv')
    # Join w/ GDP numbers
    pivot_table = pivot_table.join(gdps_df, how='inner')
    pivot_table['pct_gdp'] = (pivot_table['interest_payment'] / pivot_table['gdp_millions_end_of_year']).round(5)
    print(pivot_table.head())
    print(f"Pivot table dtypes:\n{pivot_table.dtypes}")

    # Save output
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

    # Initialize argument parser and add arguments.
    parser = argparse.ArgumentParser(description='Process the arguments for debt management.')
    parser.add_argument('--new-debt', action='store_true', help='Flag to issue new debt (default: false)')
    parser.add_argument('--fiscal-calendar', action='store_true', help='Flag to use fiscal calendar (default: false)')
    parser.add_argument('--interest-rates', type=json.loads, default=config['simulation']['interest_rates_default'],
                        help='Dictionary of interest rates with term as key and rate as value (default is 5 percent for all securities).')
    parser.add_argument('--gdp-millions', type=int, default=config['simulation']['gdp_millions'],
                        help='Current US GDP in millions of dollars.')
    parser.add_argument('--gdp-growth-rate', type=float, default=config['simulation']['gdp_growth_rate'],
                        help='Estimated GDP growth rate.')
    parser.add_argument('--new-debt-pct-gdp', type=float, default=config['simulation']['new_debt_pct_gdp'],
                        help='Estimated budget deficit.')
    parser.add_argument('--new-debt-interest-rate', type=float, default=config['simulation']['new_debt_interest_rate'],
                        help='Estimated average Fed Funds rate.')

    args = parser.parse_args()

    # Convert interest rates keys from str to int.
    interest_rates_converted = {int(k): v for k, v in args.interest_rates.items()}

    main(
        raw_data_path=config['io']['raw_data_path'],
        historical_gdps_path=config['io']['historical_gdps_path'],
        output_path=config['io']['output_path'],
        reissue_end_date=pd.to_datetime(config['simulation']['reissue_end_date']),
        new_debt=args.new_debt, 
        security_types=config['simulation']['security_types'],
        fiscal_calendar=args.fiscal_calendar, 
        interest_rates=interest_rates_converted,
        gdp_millions=args.gdp_millions,
        gdp_growth_rate=args.gdp_growth_rate,
        new_debt_pct_gdp=args.new_debt_pct_gdp,
        new_debt_interest_rate=args.new_debt_interest_rate,
        multiplier=config['simulation']['multiplier']
    )