import os
import sys
import json
import pandas as pd
import pyarrow
import argparse
from datetime import datetime
from typing import Dict
from utils import load_config, calculate_laubach_interest_rate, plot_and_save, plot_stacked_area_and_save, calculate_fraction_of_year_remaining
from simulation import calculate_interest_payments_current_year, reissue_security, issue_new_debt, compute_future_gdps

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
        interest_rates_bills: Dict[int, float],
        initial_gdp_millions: int,
        initial_debt_millions: int,
        gdp_growth_rate: float,
        primary_deficit_pct_gdp: float,
        long_term_interest_rate: float,
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
        args=(initial_yields, interest_rates_bills, reissue_end_date, laubach_rates,)).tolist()
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

    # Interest must be continually paid on all new debt assuming a consistent deficit
    # Loop by year
    data = dict()
    previous_gdp = 1
    previous_debt = 1
    previous_debt_to_gdp = 1
    previous_interest_rate = 1
    for year in range(max_record_date.year, reissue_end_date.year + 1):
        print(f"\n*****{year}*****")
        print(f"Debt: {int(current_debt)}; Pct gain: {round((current_debt - previous_debt) / previous_debt, 4)*100}")
        print(f"GDP: {int(current_gdp)}; Pct gain: {round((current_gdp - previous_gdp) / previous_gdp, 4)*100}")
        print(f"Debt-to-GDP: {round(current_debt_to_gdp, 2)}; Pct gain: {round((current_debt_to_gdp - previous_debt_to_gdp) / previous_debt_to_gdp, 4)*100}")

        # Change debt and GDP numbers to approximate value at year-end
        primary_deficit = current_gdp * (primary_deficit_pct_gdp/100)
        if year == max_record_date.year:
            current_debt += primary_deficit * calculate_fraction_of_year_remaining(max_record_date.month, max_record_date.day)
            current_gdp += primary_deficit * calculate_fraction_of_year_remaining(max_record_date.month, max_record_date.day)
            current_debt_to_gdp = current_debt / current_gdp
        # Calculate interest rate for the year
        if (laubach_rates) and (year != max_record_date.year):
            current_interest_rate = calculate_laubach_interest_rate(
                current_debt_to_gdp=current_debt_to_gdp,
                previous_debt_to_gdp=previous_debt_to_gdp,
                previous_interest_rate=previous_interest_rate,
                laubach_ratio=laubach_ratio
            )
        else:
            try:
                current_interest_rate = interest_rates_bills[year]
            except KeyError:
                current_interest_rate = interest_rates_bills[9999]
        print(f"Current interest rate: {round(current_interest_rate, 2)}")

        # Fill interest_rate and yield for securities reissued this year
        df.loc[df['year_issued'] == year, 'Interest Rate'] = current_interest_rate
        df.loc[df['year_issued'] == year, 'Yield'] = current_interest_rate

        # Calculate interest expense for this year
        # Has to include active securities, not just ones issued this year
        df_year = df[(df['year_issued'] <= year) & (df['year_matured'] >= year)]
        print(f"Number of securities active this year: {len(df_year)}")
        interest_expense_list = df_year.apply(
            func=calculate_interest_payments_current_year,
            axis=1,
            args=(year,)
        ).tolist()

        # Inspect
        if year%10 == 0:
            df_year['interest_expense'] = interest_expense_list
            df_year.to_csv(f'df_{year}.csv')

        # Sum the expenses for the year and apply multiplier
        print(f"Length of interest expense: {len(interest_expense_list)}")
        #total_interest_expense_existing = int(sum(interest_expense_list)) * multiplier
        interest_expense_existing_and_reissued = int(sum(interest_expense_list)) * multiplier
        print(f"Total interest expense on existing & reissued debt: {int(interest_expense_existing_and_reissued)}")

        # Issue new debt to cover increase from last year
        # NOTE: this method assumes all new debt for year is issued on Jan. 1, may need to fix
        # NOTE: quick fix may be divide by 2? Avg time in existence should be 6mo
        if new_debt:
            # Current year
            # Divide by 2 is a shortcut for evenly issuing the debt throughout the year;
            # average time issued this year would be 6 months
            current_year_debt_increase = (current_debt - previous_debt) / 2
            # Previous years
            previous_years_total_debt_increase = current_debt - current_year_debt_increase - initial_debt_millions
            # Combined
            total_debt_increase = current_year_debt_increase + previous_years_total_debt_increase
            # Interest expense from new debt (not counting existing/reissued)
            interest_expense_from_new_debt = total_debt_increase * (current_interest_rate/100)
            # Total interest expense components
            ## Interest expense paid on total debt increase
            ## Interest expense paid on securities existing on or before max_record_date which consists of both 'existing' and 'reissued'
            total_interest_expense = interest_expense_from_new_debt \
                + interest_expense_existing_and_reissued
        else:
            total_interest_expense = interest_expense_existing_and_reissued

        print(f"Interest expense paid on new debt: {int(interest_expense_from_new_debt)}")
        print(f"Interest expense paid on securities existing on or before max_record_date: {int(interest_expense_existing_and_reissued)}")
        print(f"Total interest expense this year: {int(total_interest_expense)}")
        print(f"Total interest expense this year as share of GDP: {round(total_interest_expense/current_gdp, 3)}")

        # Store data
        data[year] = {
            'gdp': current_gdp,
            'debt': current_debt,
            'debt_to_gdp': current_debt_to_gdp,
            'primary_deficit': primary_deficit,
            'interest_rate': current_interest_rate,
            'interest_expense_existing_and_reissued': interest_expense_existing_and_reissued,
            'interest_expense_from_new_debt': interest_expense_from_new_debt,
            'interest_expense_total': total_interest_expense,
            'interest_expense_existing_and_reissued_pct_gdp': round(interest_expense_existing_and_reissued/current_gdp, 4), 
            'interest_expense_from_new_debt_pct_gdp': round(interest_expense_from_new_debt/current_gdp, 4), 
            'total_interest_expense_pct_gdp': round(total_interest_expense/current_gdp, 4),
            'primary_deficit_pct_gdp': primary_deficit_pct_gdp
        }

        # Set 'previous_' variables for next year
        previous_gdp = current_gdp
        previous_debt = current_debt
        previous_debt_to_gdp = current_debt_to_gdp
        previous_interest_rate = current_interest_rate

        # Increment GDP and debt for next year
        current_gdp += current_gdp*(gdp_growth_rate/100)
        current_debt += primary_deficit
        current_debt += total_interest_expense
        current_debt_to_gdp = current_debt / current_gdp
    
    result = pd.DataFrame.from_dict(data, orient='index')
    result.to_csv('result.csv')

    ######### Plots
    filename_head = f"plot-debt{str(initial_debt_millions)}-gdp{str(initial_gdp_millions)}-int{str(long_term_interest_rate*100)}"
    if new_debt:
        filename_head += "-newdebt"
    if laubach_rates:
        filename_head += "-laubach"
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Line plot
    filename = filename_head + timestamp + ".png"
    plot_and_save(
        df=result,
        x_col='',
        y_cols=['total_interest_expense_pct_gdp'],
        filename=filename,
        use_index=True
    )

    # Area plot of interest expense as share of GDP
    filename = "interest-pct-gdp-" + filename_head + timestamp + ".png"
    plot_stacked_area_and_save(
        df=result,
        x_col='',
        y_cols=[
            'interest_expense_existing_and_reissued_pct_gdp', 
            'interest_expense_from_new_debt_pct_gdp',
        ],
        filename=filename,
        use_index=True
    )

    # Area plot of interest expense in millions of dollars
    filename = "interest-total-" + filename_head + timestamp + ".png"
    plot_stacked_area_and_save(
        df=result,
        x_col='',
        y_cols=[
            'interest_expense_existing_and_reissued', 
            'interest_expense_from_new_debt',
        ],
        filename=filename,
        use_index=True
    )

    # Area plot of gdp, debt, and interest expense 
    filename = "gdpdebt-" + filename_head + timestamp + ".png"
    plot_and_save(
        df=result,
        x_col='',
        y_cols=[
            'gdp', 
            'debt',
            'interest_expense_total'
        ],
        filename=filename,
        use_index=True
    )

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
    parser.add_argument('--interest-rates-bills', type=json.loads, default=config['simulation']['interest_rates_bills'],
                        help='Dictionary of interest rates by year. Use key 9999 for years not included.')
    parser.add_argument('--initial-gdp-millions', type=int, default=config['simulation']['initial_gdp_millions'],
                        help='Current US GDP in millions of dollars.')
    parser.add_argument('--initial-debt-millions', type=int, default=config['simulation']['initial_debt_millions'],
                        help='Current US debt in millions of dollars.')
    parser.add_argument('--gdp-growth-rate', type=float, default=config['simulation']['gdp_growth_rate'],
                        help='Estimated GDP growth rate.')
    parser.add_argument('--primary-deficit-pct-gdp', type=float, default=config['simulation']['primary_deficit_pct_gdp'],
                        help='Estimated budget deficit.')
    parser.add_argument('--long-term-interest-rate', type=float, default=config['simulation']['long_term_interest_rate'],
                        help='Estimated average Fed Funds rate.')

    args = parser.parse_args()

    # Convert interest rates keys from str to int.
    initial_yields_converted = {int(k): v for k, v in args.initial_yields.items()}
    interest_rates_bills_converted = {int(k): v for k, v in args.interest_rates_bills.items()}

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
        interest_rates_bills=interest_rates_bills_converted,
        initial_gdp_millions=args.initial_gdp_millions,
        initial_debt_millions=args.initial_debt_millions,
        gdp_growth_rate=args.gdp_growth_rate,
        primary_deficit_pct_gdp=args.primary_deficit_pct_gdp,
        long_term_interest_rate=args.long_term_interest_rate,
        multiplier=config['simulation']['multiplier']
    )