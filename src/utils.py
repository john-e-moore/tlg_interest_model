import yaml
import pandas as pd
import matplotlib.pyplot as plt
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
    print(f"Previous debt-to-gdp: {previous_debt_to_gdp}")
    print(f"Previous interest rate: {previous_interest_rate}")
    print(f"Current debt-to-gdp: {current_debt_to_gdp}")
    pct_gain_debt_to_gdp = (current_debt_to_gdp - previous_debt_to_gdp)/previous_debt_to_gdp
    print(f"Pct gain: {pct_gain_debt_to_gdp}")
    new_rate = previous_interest_rate + pct_gain_debt_to_gdp*laubach_ratio*100
    print(f"New rate: {new_rate}")
    return previous_interest_rate + pct_gain_debt_to_gdp*laubach_ratio*100

################################################################################
#
################################################################################
def plot_and_save(df, x_col, y_cols, filename, use_index=False):
    """
    Plots multiple lines for an arbitrary number of columns in a pandas DataFrame and saves the plot as a PNG image.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data to plot.
    x_col (str): The name of the column to use for the x-axis.
    y_cols (list): A list of column names to plot on the y-axis.
    filename (str): The name of the output image file (with .png extension).
    use_index (bool): Whether to use the DataFrame index as the x-axis. Default is False.
    """
    plt.figure(figsize=(10, 6))
    
    if use_index:
        for col in y_cols:
            plt.plot(df.index, df[col], marker='o', linestyle='-', label=col)
        plt.xlabel('Index')
    else:
        for col in y_cols:
            plt.plot(df[x_col], df[col], marker='o', linestyle='-', label=col)
        plt.xlabel(x_col)
    
    plt.ylabel('Values')
    plt.title('Multiple Lines Plot')
    plt.legend(title="Columns")
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

################################################################################
#
################################################################################
def plot_stacked_area_and_save(df, x_col, y_cols, filename, use_index=False):
    """
    Plots a stacked area chart for an arbitrary number of columns in a pandas DataFrame and saves the plot as a PNG image.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data to plot.
    x_col (str): The name of the column to use for the x-axis.
    y_cols (list): A list of column names to stack on the y-axis.
    filename (str): The name of the output image file (with .png extension).
    use_index (bool): Whether to use the DataFrame index as the x-axis. Default is False.
    """
    plt.figure(figsize=(10, 6))
    
    if use_index:
        df[y_cols].plot.area(ax=plt.gca(), stacked=True)
        plt.xlabel('Index')
    else:
        df.plot.area(x=x_col, y=y_cols, ax=plt.gca(), stacked=True)
        plt.xlabel(x_col)
    
    plt.ylabel('Values')
    plt.title('Stacked Area Chart')
    plt.legend(title="Columns", loc="upper left")
    plt.grid(True)
    plt.savefig(filename)
    plt.close()