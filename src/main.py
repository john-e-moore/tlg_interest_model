import sys
import time
import yaml
import numpy as np
import pandas as pd
import pyarrow

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def calculate_fraction_of_year_remaining(_month: int, _day: int) -> float:
    """Use for issuing year."""
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total_days_in_year = 365

    # Calculate total number of days that have passed in the year up to the given date.
    days_passed = sum(days_in_month[:_month - 1]) + _day

    return (total_days_in_year - days_passed) / total_days_in_year

def calculate_fraction_of_year_elapsed(_month: int, _day: int) -> float:
    """Use for maturing year."""
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total_days_in_year = 365

    # Calculate total number of days that have passed in the year up to the given date.
    days_passed = sum(days_in_month[:_month - 1]) + _day

    return days_passed / total_days_in_year

def calculate_fraction_of_year_between_issue_and_maturity(issue_date, maturity_date) -> float:
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

def find_closest_value(number: float, values: list) -> int:
    """
    Used to find interest rate value from dictionary. Takes
    the term in years of the security, then matches it to the nearest
    integer in 'values' (the keys of interest_rates_dict)
    """
    diffs = list(map(lambda x: abs(x - number), values))
    return min(diffs)

def reissue_security(row, interest_rates_dict, max_record_date) -> pd.DataFrame:
    """
    All securities issued before max_record_date are already in the data,
    so we start reissuing one day later.

    Returns DataFrame
    """
    # Initialize variables
    reissue_start_date = max_record_date + pd.Timedelta(days=1)
    reissue_end_date = pd.to_datetime('2049-12-31')
    ## Calculate interest rate from term
    term_days = row['term_days']
    term_years = term_days / 365
    interest_rate = find_closest_value(term_years, list(interest_rates_dict.keys()))
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

    # TODO: from now to 2050, when a security matures, reissue it (add a row)
    # for the same term at a 5% interest rate (should be parameter)
    # The multiple row securities should be reissued for the full
    # outstanding amount.
    # Iterate one day at a time, starting at max 'record date'
    # df = df[df['Maturity Date'] == date]
    # Add new row with all the columns
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
        1: .05, # 1 year or less
        2: .05,
        3: .05,
        5: .05,
        7: .05,
        10: .05,
        20: .05,
        30: .05
    }
    # Apply reissue function here (will return Series of Dataframes)
    #test_df = df[df['Security Class 1 Description'] == 'Bills Maturity Value'].reset_index()
    #test_df = df[df['Security Class 2 Description'] == '912796MH9']
    #print(f"Number of securities in test data before reissuing: {len(test_df)}")
    print("Simulating reissuance...")
    # TODO: can't figure out why .apply was taking so long; use for loop
    # and then try .apply again.
    """
    test_reissue = test_df.apply(
        func=reissue_security,
        axis=1,
        args=(interest_rates_dict, max_record_date))
    """
    start_time = time.time()
    cum_rows = 0
    df_list = []
    for i,row in df.iterrows():
        x = reissue_security(row, interest_rates_dict, max_record_date)
        cum_rows += len(x)
        df_list.append(x)
        if (i+1)%500 == 0:
            print(f"{i+1} records processed. Cumulative rows: {cum_rows}")
        #time.sleep(1)
    end_time = time.time()
    print(f"Simulating reissuance took {(end_time - start_time) / 60} minutes.")
    print("Complete. Concatenating results...")
    #test_reissue_result = pd.concat(test_reissue.tolist(), axis=0, ignore_index=True)
    reissue_result = pd.concat(df_list, axis=0, ignore_index=True)
    print("Complete.")
    print(f"Number of reissued securities in test data: {len(reissue_result)}")
    total_memory_gb = reissue_result.memory_usage(deep=True).sum() / (1024*3)
    print(f"Memory usage: {total_memory_gb}")
    reissue_result.to_csv('test_reissue_result.csv')

    # TODO: Concat the new dataframes with the original one.
    df = pd.concat([df, reissue_result], axis=0, ignore_index=True)
    print(f"Number of rows after combining: {len(df)}")

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
    start_time = time.time()
    print(f"Processing rows took {(end_time - start_time) / 60} minutes.")

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
    pivot_table.to_csv('result.csv')


    # TODO: split code into reissuance and interest payments modules


if __name__ == "__main__":
    main()