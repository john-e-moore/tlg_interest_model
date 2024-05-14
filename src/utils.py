import yaml
import pandas as pd
from typing import List, Union

def load_config(config_path: str) -> dict:
    """Load config from yml file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

################################################################################
#
################################################################################
    
def find_closest_value_index(number: float, values: List[Union[int, float]]) -> int:
    """
    Used to find interest rate value from dictionary. Takes
    the term in years of the security, then matches it to the index of 
    the nearest integer in 'values' (the keys of interest_rates_dict)
    """
    diffs = list(map(lambda x: abs(x - number), values))
    return diffs.index(min(diffs))

################################################################################
#
################################################################################
  
def calculate_fraction_of_year_remaining(_month: int, _day: int) -> float:
    """Use for issuing year."""
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total_days_in_year = 365

    # Calculate total number of days that have passed in the year up to the given date.
    days_passed = sum(days_in_month[:_month - 1]) + _day

    return (total_days_in_year - days_passed) / total_days_in_year

################################################################################
#
################################################################################

def calculate_fraction_of_year_elapsed(_month: int, _day: int) -> float:
    """Use for maturing year."""
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total_days_in_year = 365

    # Calculate total number of days that have passed in the year up to the given date.
    days_passed = sum(days_in_month[:_month - 1]) + _day

    return days_passed / total_days_in_year

################################################################################
#
################################################################################

def calculate_fraction_of_year_between_issue_and_maturity(
        issue_date: pd.Timestamp, 
        maturity_date: pd.Timestamp) -> float:
    """
    Use when Issue Date and Maturity Date are in the same calendar year.

    Parameters:
    issue_date: Pandas Datetime object
    maturity_date: Pandas Datetime object

    Returns: float (fraction of a year)
    """
    if issue_date.year != maturity_date.year:
        raise ValueError("Dates must be within the same year when using calculate_fraction_of_year_between.")
    
    days_between = (maturity_date - issue_date).days
    total_days_in_year = 365
    
    return days_between / total_days_in_year

################################################################################
#
################################################################################

def calculate_laubach_interest_rate(
        current_debt_to_gdp: float, 
        previous_debt_to_gdp: float, 
        previous_interest_rate: float,
        laubach_ratio: float) -> float:
    """
    Calculates theoretical underlying interest rate based on debt-to-gdp.

    Parameters:
    debt: current debt
    gdp: current gdp
    laubach_ratio: marginal gain in theoretical underlying interest rate,
      in basis points, per point of debt-to-gdp gain 

    Returns: theoretical underlying interest rate
    """
    pct_gain_debt_to_gdp = (current_debt_to_gdp - previous_debt_to_gdp)/previous_debt_to_gdp
    
    return previous_interest_rate + pct_gain_debt_to_gdp*laubach_ratio