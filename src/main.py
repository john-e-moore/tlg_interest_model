def main():
    """
    Objective: Calculate US Gov't debt burden thru 2030.

    Assumptions:
    * 5% interest rate when debt gets reissued.
    * All debts get reissued immediately when the mature.
    """

    # 1. Read data from data/MSPD_DetailSecty*.csv.
    # 1a. Remove records with Maturity Date <= Issue Date
    # 2. Collapse on 'Security Class 2 Description' aka unique ID
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
    pass

if __name__ == "__main__":
    main()