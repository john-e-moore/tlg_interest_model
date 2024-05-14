import os
import sys
import json
import pandas as pd
import pyarrow
import argparse
from typing import Dict
from utils import load_config, calculate_laubach_interest_rate
from simulation import calculate_interest_payments, reissue_security, issue_new_debt, compute_future_gdps

def main(
        raw_data_path: str,
        historical_gdps_path: str,
        output_path: str,
        reissue_end_date: pd.Timestamp,
        new_debt: bool, 
        laubach_rates: bool,
        laubach_ratio: float,
        security_types: list,
        fiscal_calendar: bool, 
        initial_yields: Dict[int, float],
        initial_gdp_millions: int,
        initial_debt_millions: int,
        gdp_growth_rate: float,
        primary_deficit_pct_gdp: float,
        initial_interest_rate: float,
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
        args=(initial_yields, reissue_end_date, laubach_rates,)).tolist()
    print("Complete. Concatenating results...")
    reissue_result = pd.concat(reissue_list, axis=0, ignore_index=True)
    print("Complete.")
    print(f"Number of reissued securities in data: {len(reissue_result)}")

    # Concatenate the new dataframes with the original one.
    df = pd.concat([df, reissue_result], axis=0, ignore_index=True)
    print(f"Number of rows after combining: {len(df)}")

    df.to_csv('reissued_no_rates.csv')


    ################################################################################
    # Main simulation
    ################################################################################
    # Add year, month, day columns for interest payment calculation.
    df['year_issued'] = df['Issue Date'].dt.year
    df['month_issued'] = df['Issue Date'].dt.month
    df['day_issued'] = df['Issue Date'].dt.day
    df['year_matured'] = df['Maturity Date'].dt.year
    df['month_matured'] = df['Maturity Date'].dt.month
    df['day_matured'] = df['Maturity Date'].dt.day
    # Initialize variables for loop
    current_debt = initial_debt_millions
    current_gdp = initial_gdp_millions
    current_debt_to_gdp = initial_debt_millions / initial_gdp_millions
    current_interest_rate = initial_interest_rate
    cumulative_interest_payments = 0
    # Loop by year
    for year in range(max_record_date.year, reissue_end_date.year + 1):
        print(f"*****{year}*****")
        print(f"Debt: {int(current_debt)}")
        print(f"GDP: {int(current_gdp)}")
        print(f"Debt-to-GDP: {round(current_debt_to_gdp, 2)}")
        # NOTE: make sure to account for fractional years in interest payment calc.
        if (laubach_rates) and (year != max_record_date.year):
            current_interest_rate = calculate_laubach_interest_rate(
                current_debt_to_gdp=current_debt_to_gdp,
                previous_debt_to_gdp=previous_debt_to_gdp,
                previous_interest_rate=previous_interest_rate,
                laubach_ratio=laubach_ratio
            )
        print(f"Current interest rate: {round(current_interest_rate, 2)}")
        # Fill interest_rate and yield for securities reissued this year
        if laubach_rates:
            df.loc[df['year_issued'] == year, 'Interest Rate'] = current_interest_rate
            df.loc[df['year_issued'] == year, 'Yield'] = current_interest_rate
        # Set 'previous_' variables for next year
        previous_debt_to_gdp = current_debt_to_gdp
        previous_interest_rate = current_interest_rate

        # Calculate interest expense for this year
        # Apply function to each row
        # On df
        ## if it got issued this year, calculate fraction of year

        # Increment GDP and debt
        # GDP increases proportional to gdp_growth_rate from config
        current_gdp += current_gdp*(gdp_growth_rate/100)
        # Debt increases by primary_deficit*current_gdp + interest_expense_current_year
        current_debt += current_gdp*(primary_deficit_pct_gdp/100)
        # TODO: current_debt += interest_expense_this_year
        current_debt_to_gdp = current_debt / current_gdp
        # NOTE: do NOT need to keep running interest expense for the calculation
        # since it gets added to debt at end of each year
    # If laubach_rates:
    #  Calculate debt-to-gdp
    #  Calculate interest rate
    #  Fill in interest rate / yield for all securities getting reissued that year
    # Create new debt equal to primary deficit with current interest rate
    #  ## issue_new_debt function cannot be used; looping years takes place in main now
    # Calculate interest expense for current year, then add it to cumulative debt
    df.to_csv('laubach_rates_filled.csv')

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
    parser.add_argument('--laubach-rates', action='store_true', help='Flag to calculate interest rates based on debt-to-gdp (default: false)')
    parser.add_argument('--fiscal-calendar', action='store_true', help='Flag to use fiscal calendar (default: false)')
    parser.add_argument('--initial-yields', type=json.loads, default=config['simulation']['initial_yields'],
                        help='Dictionary of yields with term as key and rate as value (default is 5 percent for all securities).')
    parser.add_argument('--initial-gdp-millions', type=int, default=config['simulation']['initial_gdp_millions'],
                        help='Current US GDP in millions of dollars.')
    parser.add_argument('--initial-debt-millions', type=int, default=config['simulation']['initial_debt_millions'],
                        help='Current US debt in millions of dollars.')
    parser.add_argument('--gdp-growth-rate', type=float, default=config['simulation']['gdp_growth_rate'],
                        help='Estimated GDP growth rate.')
    parser.add_argument('--primary-deficit-pct-gdp', type=float, default=config['simulation']['primary_deficit_pct_gdp'],
                        help='Estimated budget deficit.')
    parser.add_argument('--initial-interest-rate', type=float, default=config['simulation']['initial_interest_rate'],
                        help='Estimated average Fed Funds rate.')

    args = parser.parse_args()

    # Convert interest rates keys from str to int.
    initial_yields_converted = {int(k): v for k, v in args.initial_yields.items()}

    main(
        raw_data_path=config['io']['raw_data_path'],
        historical_gdps_path=config['io']['historical_gdps_path'],
        output_path=config['io']['output_path'],
        reissue_end_date=pd.to_datetime(config['simulation']['reissue_end_date']),
        new_debt=args.new_debt, 
        laubach_rates=args.laubach_rates,
        laubach_ratio=config['simulation']['laubach_ratio'],
        security_types=config['simulation']['security_types'],
        fiscal_calendar=args.fiscal_calendar, 
        initial_yields=initial_yields_converted,
        initial_gdp_millions=args.initial_gdp_millions,
        initial_debt_millions=args.initial_debt_millions,
        gdp_growth_rate=args.gdp_growth_rate,
        primary_deficit_pct_gdp=args.primary_deficit_pct_gdp,
        initial_interest_rate=args.initial_interest_rate,
        multiplier=config['simulation']['multiplier']
    )