import numpy as np
import pandas as pd
from utils import find_closest_value_index, calculate_fraction_of_year_remaining, calculate_fraction_of_year_elapsed, calculate_fraction_of_year_between_issue_and_maturity

def compute_future_gdps(
    gdp_millions: int,
    gdp_growth_rate: float,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp
) -> dict:
    gdps = {}
    start_year = start_date.year
    end_year = end_date.year
    current_gdp = gdp_millions

    for year in range(start_year, end_year + 1):
        gdps[str(year)] = current_gdp
        current_gdp *= (1 + (gdp_growth_rate / 100))
    
    return gdps

def issue_new_debt(
    gdp_millions: int,
    gdp_growth_rate: float,
    new_debt_pct_gdp: float,
    interest_rate: float,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp
) -> dict:
    """
    Note: Percentages are passed as percents and need to be divided by 100 for calculations.
    
    Note: The interest payments are added cumulatively year by year; new debt issued
    each year stays on the books. 

    Params:
    gdp_millions: US GDP in millions of dollars.
    gdp_growth_rate: The yearly rate of GDP growth to use.
    new_debt_pct_gdp: The amount of new debt every year as a percentage of GDP.
    interest_rate: The yearly interest rate to be paid on new debt.
    start_date: Start date.
    end_date: End date.

    Returns:
    Dictionary in the form {year: interest_payment} where year an integer
    and interest_payment is the interest paid that year.
    """
    interest_payments = {}
    start_year = start_date.year
    end_year = end_date.year
    current_gdp = gdp_millions

    cumulative_debt = 0
    for year in range(start_year, end_year + 1):
        new_debt = (current_gdp * new_debt_pct_gdp) / 100
        interest_payment = (new_debt * interest_rate) / 100

        # Prorate start year and end year payments
        if year == start_year:
            interest_payment *= calculate_fraction_of_year_remaining(
                start_date.month, start_date.day
            )
        elif year == end_year:
            interest_payment *= calculate_fraction_of_year_elapsed(
                end_date.month, end_date.day
            )

        interest_payments[str(year)] = interest_payment + cumulative_debt

        current_gdp *= (1 + (gdp_growth_rate / 100))
        cumulative_debt += interest_payment

    return interest_payments

################################################################################
#
################################################################################

def reissue_security(
        row: pd.Series, 
        interest_rates: dict, 
        reissue_end_date: pd.Timestamp) -> pd.DataFrame:
    """
    All securities issued before max_record_date are already in the data,
    so we start reissuing one day later.

    Returns DataFrame
    """
    # Initialize variables
    ## Calculate interest rate from term
    term_days = row['term_days']
    term_years = term_days / 365
    closest_term_years_index = find_closest_value_index(term_years, list(interest_rates.keys()))
    closest_term_years = list(interest_rates.keys())[closest_term_years_index]
    interest_rate = interest_rates.get(closest_term_years)
    ## Other loop variables
    security_class_1_description = row['Security Class 1 Description']
    security_class_2_description = row['Security Class 2 Description']
    issued_amount = row['Issued Amount (in Millions)']
    current_issue_date = row['Maturity Date'] + pd.Timedelta(days=1)

    # Initialize result DataFrame
    colnames = [
        'Security Class 1 Description',
        'Security Class 2 Description',
        'Interest Rate',
        'Yield',
        'Issue Date',
        'Maturity Date',
        'Issued Amount (in Millions)'
    ]
    df = pd.DataFrame(columns=colnames)

    # Fill DataFrame with securities reissued until 2050
    while current_issue_date <= reissue_end_date:
        current_maturity_date = current_issue_date + pd.Timedelta(days=term_days)
        df.loc[len(df)] = {
            'Security Class 1 Description': security_class_1_description,
            'Security Class 2 Description': security_class_2_description,
            'Interest Rate': interest_rate,
            'Yield': interest_rate,
            'Issue Date': current_issue_date,
            'Maturity Date': current_maturity_date,
            'Issued Amount (in Millions)': issued_amount
        }
        current_issue_date += pd.Timedelta(days=term_days)
    
    return df

################################################################################
#
################################################################################

def calculate_interest_payments(row: pd.Series) -> dict: 
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
        '2020': 365,
        '2021': 365,
        ...
    }
    """
    
    # Initialize variables
    ## Years, months, days
    year_issued = row['year_issued']
    month_issued = row['month_issued']
    day_issued = row['day_issued']
    year_matured = row['year_matured']
    month_matured = row['month_matured']
    day_matured = row['day_matured']
    ## Issued amount
    issue_amount = row['Issued Amount (in Millions)']
    ## Is the security same-year or multi-year?
    if year_issued == year_matured:
        is_multi_year = False
    else:
        is_multi_year = True
    ## Bonds and Notes use interest rate. Bills don't have one; use yield.
    if not np.isnan(row['Interest Rate']):
        interest_rate = row['Interest Rate'] / 100

    else:
        interest_rate = row['Yield'] / 100
    
    # Initialize result dictionary
    result = {
        'id': row['Security Class 2 Description'],
        'security_type': row['Security Class 1 Description'],
        'issue_date': row['Issue Date'],
        'maturity_date': row['Maturity Date']
    }
    
    # Calculate interest payment for same-year securities.
    if not is_multi_year:
        issue_date = row['Issue Date']
        maturity_date = row['Maturity Date']
        fraction_of_year_between_issue_and_maturity = calculate_fraction_of_year_between_issue_and_maturity(issue_date, maturity_date)
        interest_payment = fraction_of_year_between_issue_and_maturity * issue_amount * interest_rate
        # Update dictionary
        result[str(year_issued)] = interest_payment

    # Calculate interest payments for multi-year securities.
    if is_multi_year:
        fraction_of_year_remaining_after_issue = calculate_fraction_of_year_remaining(month_issued, day_issued)
        fraction_of_year_elapsed_before_maturity = calculate_fraction_of_year_elapsed(month_matured, day_matured)
        for _year in range(year_issued, year_matured+1):
            if _year == year_issued:
                interest_payment = fraction_of_year_remaining_after_issue * issue_amount * interest_rate
            elif _year == year_matured:
                interest_payment = fraction_of_year_elapsed_before_maturity * issue_amount * interest_rate
            else: # Full year
                interest_payment = issue_amount * interest_rate
            # Update dictionary
            result[str(_year)] = interest_payment
    
    return result