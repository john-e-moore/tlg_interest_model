import yaml
import numpy as np
import pandas as pd
import pyarrow

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def calculate_fraction_of_year_remaining(_month: int, _day: int):
    """Use for issuing year."""
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total_days_in_year = 365

    # Calculate total number of days that have passed in the year up to the given date.
    days_passed = sum(days_in_month[:_month - 1]) + _day

    return (total_days_in_year - days_passed) / total_days_in_year

def calculate_fraction_of_year_elapsed(_month: int, _day: int):
    """Use for maturing year."""
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total_days_in_year = 365

    # Calculate total number of days that have passed in the year up to the given date.
    days_passed = sum(days_in_month[:_month - 1]) + _day

    return days_passed / total_days_in_year

def process_raw_row(row): 
    """
    Iterates through the years a security was live and returns a dictionary
    containing the interest payment for each year.

    Parameters:
    row: A single row of a Pandas DataFrame

    Returns:
    {
        id: 938848,
        security_type: bond,
        initial_issue_date: 1/1/2020,
        maturity_date: 1/1/2024,
        interest_paid:
        {
            2020: 80,
            2021: 100,
            2022: 100,
            2023: 100,
            2024: 20
        }
    }
    """
    # Create a dict with keys being years between issue and maturity, inclusive.
    year_issued = row['year_issued']
    year_matured = row['year_matured']
    interest_payments = {x: 0 for x in range(year_issued, year_matured+1)}

    # Calculate year fractions for issue and mature years. 
    month_issued = row['month_issued']
    day_issued = row['day_issued']
    month_matured = row['month_matured']
    day_matured = row['day_matured']
    fraction_of_year_remaining_after_issue = calculate_fraction_of_year_remaining(month_issued, day_issued)
    fraction_of_year_elapsed_before_maturity = calculate_fraction_of_year_elapsed(month_matured, day_matured)

    # Initialize interest rate variable.
    # Bonds and Notes use interest rate. Bills don't have one; use yield.
    if not np.isnan(row['Interest Rate']):
        interest_rate = row['Interest Rate'] / 100

    else:
        interest_rate = row['Yield'] / 100

    # Calculate interest payments and update dict. 
    issue_amount = row['Issued Amount (in Millions)']
    for i,_year in enumerate(interest_payments.keys()):
        if i == 0: # Year issued
            interest_payment = fraction_of_year_remaining_after_issue * issue_amount * interest_rate
        elif i == len(interest_payments.keys()) - 1: # Year matured
            interest_payment = fraction_of_year_elapsed_before_maturity * issue_amount * interest_rate
        else: # Full year
            interest_payment = issue_amount * interest_rate
        # Update dictionary
        interest_payments.update({_year: interest_payment})
    
    return {
        'id': row['Security Class 2 Description'],
        'security_type': row['Security Class 1 Description'],
        'issue_date': row['Issue Date'],
        'maturity_date': row['Maturity Date'],
        'interest_paid': interest_payments
    }


def main():
    """
    Objective: Calculate US Gov't debt burden thru 2030.

    Assumptions:
    * 5% interest rate when debt gets reissued.
    * All debts get reissued immediately when the mature.
    """

    # 1. Read data from data/MSPD_DetailSecty*.csv.
    # 1a. Remove records with Maturity Date <= Issue Date
    # 2. *** This is wrong, get more info from Joe Collapse on 'Security Class 2 Description' aka unique ID
    ## using average of yields weighted by issued amount.
    # 3. Add columns to collapsed dataframe for each calendar year
    ## and fill with interest to be paid on that debt for that year.
    ## df['days_remaining_in_issue_year'] = ...
    ## df['days_to_maturity_in_mature_year'] = ...
    ## df['2018_interest_paid] = ...
    ## df['2019_interest_paid] = ...
    # 4. Make a pivot table summing each calendar year's interest
    ## payment column, and also add a cumulative sum column.

    """
    Example: 
    Issue date: 10/31/2018
    Maturity date: 10/31/2020
    Interest rate: 3
    Yield: 3.074
    Issued amount (millions): 31000

    interest_paid_in_2018 = (62 / 365) * .03074 * 31,000,000,000
    interest_paid_in_2019 = (365 / 365) * .03074 * 31,000,000,000
    interest_paid_in_2020 = (303 / 365) * .03074 * 31,000,000,000

    note: 62 is the number of days left in the calendar year 2018
    """
    
    # Load config
    config_path = '/home/john/tlg/interest_model/src/config.yml'
    config = load_config(config_path)

    # Read data
    usecols = [
        'Security Type Description', # Marketable or Non-Marketable
        'Security Class 1 Description', # Type of security
        'Security Class 2 Description', # CUSIP ID number (unique for each security)
        'Interest Rate',
        'Yield',
        'Issue Date',
        'Maturity Date',
        'Issued Amount (in Millions)', # Read as non-numeric due to *
        'Outstanding Amount (in Millions)', # Read as non-numeric due to *
    ]
    raw_data_path = config['raw_data_path']

    df = pd.read_csv(raw_data_path, usecols=usecols)
    print(df.head())
    print(df.dtypes)
    print(df.shape)

    # Filter data
    # Only keep non-TIPS, non-FSN marketable securities
    class_1_descriptions_to_keep = ('Notes', 'Bonds', 'Bills Maturity Value')
    df = df[df['Security Class 1 Description'].isin(class_1_descriptions_to_keep)]
    print("Non-marketable securites, TIPS, and FSN's removed.")
    print(df.shape)
    # Drop duplicates
    # Raw data seems to be append-only, so same security can have multiple rows
    # But, securities can be re-issued (added onto) at a later date
    subset = ['Security Class 2 Description', 'Issue Date']
    df.drop_duplicates(subset=subset, keep='first', inplace=True)
    print("Duplicates dropped.")
    print(df.shape)
    # Remove totals
    df = df[~df['Security Class 2 Description'].str.contains('Total')]
    print("Totals records removed.")
    print(df.shape)

    # Change columns to numeric
    df['Issued Amount (in Millions)'] = pd.to_numeric(df['Issued Amount (in Millions)'])
    df['Outstanding Amount (in Millions)'] = pd.to_numeric(df['Outstanding Amount (in Millions)'])

    # Change columns to datetime after dropping nulls
    df.dropna(subset=['Issue Date', 'Maturity Date'], inplace=True) # (1)
    df['Issue Date'] = pd.to_datetime(df['Issue Date'])
    df['Maturity Date'] = pd.to_datetime(df['Maturity Date'])

    print(df[['Issue Date', 'Maturity Date']].head())
    print(df.dtypes)

    # Add year, month, day columns for interest payment calculation
    df['year_issued'] = df['Issue Date'].dt.year
    df['month_issued'] = df['Issue Date'].dt.month
    df['day_issued'] = df['Issue Date'].dt.day
    df['year_matured'] = df['Maturity Date'].dt.year
    df['month_matured'] = df['Maturity Date'].dt.month
    df['day_matured'] = df['Maturity Date'].dt.day

    # Process an example row
    result = process_raw_row(df.iloc[0,:])
    print(result)

    df.to_csv('sample.csv', index=False)
    # NOTE: Calculation needs to begin here; can't collapse data because
    # The security can be added on to. 
    # Create a function that takes a single security, iterates, and outputs
    # a dict with:
    """
    {
        id: 938848,
        security_type: bond,
        initial_issue_date: 1/1/2020,
        maturity_date: 1/1/2024,
        interest_paid:
        {
            2020: 80,
            2021: 100,
            2022: 100,
            2023: 100,
            2024: 20
        }
    }
    """
    # then create a dataframe from this dict with the necessary columns for each year









    # Collapse data
    # Group by Security Class 2 Description
    # Sum Issued Amount
    # Average Interest Rate
    grouped_df = df.groupby('Security Class 2 Description').agg({
        'Issued Amount (in Millions)': 'sum',
        'Interest Rate': 'mean',
        'Yield': 'mean'
    })
    grouped_df = df.groupby('Security Class 2 Description').agg({
        'Security Class 2 Description': 'count',
        'Issued Amount (in Millions)': 'sum',
        'Interest Rate': 'mean',
        'Yield': 'mean'
    })
    print(grouped_df.head(20))
    print(grouped_df.columns)
    print(grouped_df.shape)

    # Examine why there are still duplicate IDs
    test_df = df[df['Security Class 2 Description'] == '912757VP3']
    print(test_df)
    # Maturity dates are all the same, but issue date is not
    # 

    # Left join 

    # Add issue date calendar year

if __name__ == "__main__":
    main()