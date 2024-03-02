import sys
import time
import yaml
import numpy as np
import pandas as pd
import pyarrow
from utils import load_config, find_closest_value_index, calculate_fraction_of_year_remaining, calculate_fraction_of_year_elapsed, calculate_fraction_of_year_between_issue_and_maturity

def process_raw_row(row) -> dict: 
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

def reissue_security(row, interest_rates_dict) -> pd.DataFrame:
    """
    All securities issued before max_record_date are already in the data,
    so we start reissuing one day later.

    Returns DataFrame
    """
    # Initialize variables
    reissue_end_date = pd.to_datetime('2050-12-31')
    ## Calculate interest rate from term
    term_days = row['term_days']
    term_years = term_days / 365
    closest_term_years_index = find_closest_value_index(term_years, list(interest_rates_dict.keys()))
    closest_term_years = list(interest_rates_dict.keys())[closest_term_years_index]
    interest_rate = interest_rates_dict.get(closest_term_years)
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


def main():
    """
    Objective: Calculate US Gov't debt burden thru 2050.

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
    
    # Load config.
    config_path = '/home/john/tlg/interest_model/src/config.yml'
    config = load_config(config_path)

    # Read data.
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
    raw_data_path = config['raw_data_path']

    df = pd.read_csv(raw_data_path, usecols=usecols)
    print(df.dtypes)
    print(df.shape)

    # Filter data.
    # Only keep non-TIPS, non-FSN marketable securities.
    class_1_descriptions_to_keep = (
        'Notes', 
        'Bonds', 
        'Bills Maturity Value',
        #'Inflation-Protected Securities',
        #'Floating Rate Notes'
    )
    df = df[df['Security Class 1 Description'].isin(class_1_descriptions_to_keep)]
    print("Non-marketable securites, TIPS, and FSN's removed.")
    print(df.shape)
    # Drop duplicates.
    # Raw data seems to be append-only, so same security can have multiple rows.
    # But, securities can be re-issued (added onto) at a later date.
    subset = ['Security Class 2 Description', 'Issue Date']
    df.drop_duplicates(subset=subset, keep='first', inplace=True)
    print("Duplicates dropped.")
    print(df.shape)
    # Remove totals.
    df = df[~df['Security Class 2 Description'].str.contains('Total')]
    print("Totals records removed.")
    print(df.shape)

    # Change columns to numeric.
    df['Issued Amount (in Millions)'] = pd.to_numeric(df['Issued Amount (in Millions)'])
    #df['Outstanding Amount (in Millions)'] = pd.to_numeric(df['Outstanding Amount (in Millions)'])

    # Change columns to datetime after dropping nulls.
    df.dropna(subset=['Issue Date', 'Maturity Date'], inplace=True) # (1)
    df['Issue Date'] = pd.to_datetime(df['Issue Date'])
    df['Maturity Date'] = pd.to_datetime(df['Maturity Date'])
    df['Record Date'] = pd.to_datetime(df['Record Date'])

    # Max record date; don't need to reissue anything that matures before this.
    max_record_date = df['Record Date'].max()
    print(f"Max record date: {max_record_date}")
    df.drop('Record Date', axis=1, inplace=True)

    # Security term in days
    df['term_days'] = (df['Maturity Date'] - df['Issue Date']).dt.days
    # This line ensures the reissue function doesn't run forever
    df = df[df['term_days'] > 0]
    print("Negative term records removed.")
    print(df.shape)

    # Count how many bonds/bills/notes
    value_counts = df['Security Class 1 Description'].value_counts()
    print("Value counts:")
    print(value_counts)
    # Average bill term in days
    for description in class_1_descriptions_to_keep:
        term_avg = df['term_days'][df['Security Class 1 Description'] == description].mean()
        print(f"Average {description} term: {int(term_avg)} days")

    # TODO: store interest_rates_dict in config
    # term: rate
    interest_rates_dict = {
        1: 5, # 1 year or less
        2: 5,
        3: 5,
        5: 5,
        7: 5,
        10: 5,
        20: 5,
        30: 5
    }
    # Apply reissue function here (will return Series of Dataframes)
    # Only reissue debt that expires after max record date.
    print(f"DF length: {len(df)}")
    reissue_df = df[df['Maturity Date'] >= max_record_date].reset_index(drop=True)
    print(f"Number of securities in original data to be reissued: {len(reissue_df)}")
    print("Simulating reissuance...")
    start_time = time.time()
    reissue_list = reissue_df.apply(
        func=reissue_security,
        axis=1,
        args=(interest_rates_dict,)).tolist()
    end_time = time.time()
    print(f"Simulating reissuance took {round((end_time - start_time), 1)} seconds.")
    print("Complete. Concatenating results...")
    reissue_result = pd.concat(reissue_list, axis=0, ignore_index=True)
    print("Complete.")
    print(f"Number of reissued securities in data: {len(reissue_result)}")
    total_memory_gb = reissue_result.memory_usage(deep=True).sum() / (1024*3)
    print(f"Memory usage: {total_memory_gb}")
    reissue_result.to_csv('reissue_result.csv')

    # Concat the new dataframes with the original one.
    df = pd.concat([df, reissue_result], axis=0, ignore_index=True)
    print(f"Number of rows after combining: {len(df)}")
    df.to_csv('concat_after_reissue.csv')

    # Add year, month, day columns for interest payment calculation.
    df['year_issued'] = df['Issue Date'].dt.year
    df['month_issued'] = df['Issue Date'].dt.month
    df['day_issued'] = df['Issue Date'].dt.day
    df['year_matured'] = df['Maturity Date'].dt.year
    df['month_matured'] = df['Maturity Date'].dt.month
    df['day_matured'] = df['Maturity Date'].dt.day

    # Calculate interest payments on each security, then recombine
    # the resulting Series into a DataFrame with columns added for
    # each year's interest payments.
    start_time = time.time()
    processed_rows = df.apply(process_raw_row, axis=1)
    df_yearly = pd.DataFrame(processed_rows.tolist())
    end_time = time.time()
    print(f"Processing rows took {(end_time - start_time) / 60} minutes.")
    df_yearly.to_csv('df_yearly.csv')

    # Reorder year columns.
    year_columns = [col for col in df_yearly.columns if col.isdigit() and 1900 <= int(col) <= 2100]
    non_year_columns = [col for col in df_yearly.columns if col not in year_columns]
    sorted_year_columns = sorted(year_columns, key=lambda x: int(x))
    df_yearly_sorted = df_yearly[non_year_columns + sorted_year_columns]
    print("Sorted year columns.")
    print(df_yearly_sorted.shape)
    
    # Sum yearly interest payments by id and security type.
    df_yearly_sorted.drop(['issue_date', 'maturity_date'], axis=1, inplace=True)
    id_grouped_df = df_yearly_sorted.groupby(['id', 'security_type'], as_index=False).sum()
    print("Grouped securities by id and security type, summing yearly interest payments.")
    print(id_grouped_df.shape)

    id_grouped_df.to_csv('id_grouped.csv', index=False)

    # Pivot sum of yearly interest payments on security type.
    id_grouped_df.drop('id', axis=1, inplace=True)
    df_melted = id_grouped_df.melt(id_vars=["security_type"], var_name="year", value_name="interest_payment")
    pivot_table = pd.pivot_table(df_melted, values="interest_payment", index=["security_type", "year"], aggfunc='sum')
    pivot_table.to_csv('result_by_security_type.csv')
    # Pivot year only, not security type.
    pivot_table = pd.pivot_table(df_melted, values="interest_payment", index=["year"], aggfunc='sum')
    pivot_table['interest_payment'] = pivot_table['interest_payment'].round(2)
    pivot_table.to_csv('result.csv')


    # TODO: split code into reissuance and interest payments modules


if __name__ == "__main__":
    main()