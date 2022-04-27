# encoding: utf8

import time
import sys
import random
from tabulate import tabulate
import pandas as pd

__version__ = '0.0.1'
__author__ = 'Adrian Loo'


# Constants
DISPLAY_UNIT = 60  # Letter Space
BOOL = ['y', 1, 't', 'yes', 'true', '', ' ']


def system_ballot(input_path=None, systems=3):
    '''
    '''
    if input_path is None:
        print("Nothing to ballot")
        return None

    if total_resource is None:
        print("No resource to ballot")
        return None

    df = pd.read_csv(input_path)
    print("Configuration Start".center(DISPLAY_UNIT, '='))

    # Check for duplicate
    if any(df.duplicated()):
        # print("Duplicate Data".center(DISPLAY_UNIT, '='))
        # print(df[df.duplicated()])
        print("[WARNING] Duplicate index found, proceed to drop duplicates")
        df.drop_duplicates(inplace=True)

    print("Participants List:\n")
    print(df)


def run_draw(input_path=None, total_resource=None, resource_name='ticket', delay=1, ignore_duplicates=True):
    '''
    Takes input path to csv file and converts into pandas dataframe
    Checks for columns with unique entries and use as unique_id column to generate ballot ticktes
    Create chances from weights and populate ballot table
    Runs ballot and produces winners and loser dataframe

    Parameters:
        input_path [path]: path to csv file
        total_resources [int]: an integer value that defines to total amount of resources available for balloting
        resource_name [str]: the string name for resource, default is 'ticket'
        delay [int]: integer value for delay time in printing winning ballots during the draw

    Return:
        tuple of 4 dataframes:
            df - the original dataframe
            org_ballot_df - the ballot table before the draw starts
            winner_df - the winners dataframe
            loser_df - the loser dataframe
    '''
    if input_path is None:
        print("Nothing to ballot")
        return None

    if total_resource is None:
        print("No resource to ballot")
        return None

    df = pd.read_csv(input_path)
    print(" Configuration Start ".center(DISPLAY_UNIT, '='))

    # Check for duplicate
    if any(df.duplicated()) and not ignore_duplicates:
        if input(f"[WARNING] Duplicates found:\n{tabulate(df[df.duplicated()], tablefmt='pretty')}\nProceed to drop?[Y/n] ").lower() in BOOL:
            df.drop_duplicates(inplace=True)
            df.reset_index(drop=True, inplace=True)

    # find unique id column
    uid_col = None

    # Checks for unique identity column
    print("Checking Columns for unique data")
    for col in df.columns:
        if df[col].nunique() == len(df):
            print(col)
            uid_col = col
            if input(f"Found column with unique data - {col}.\nUse this?[Y/n] ").lower() in BOOL:
                df[uid_col] = df[uid_col].astype('str')
                break
            else:
                uid_col = None

    # Validate auto find
    if uid_col is None:
        # Check for unique identity column and try to auto create one
        df['UID'] = ['-'.join(i) for i in zip(*[df[s].map(str) for s in df.columns])]
        if df['UID'].nunique() == len(df):
            uid_col = 'UID'
            print(f"Auto generate [{uid_col}] column.")
        else:
            raise ValueError("No unique column can be created")

    # ask for weight column
    headers = ['Index', 'Column Name']
    table = []
    for i in range(len(df.columns)):
        if df.dtypes[df.columns[i]].name in ['float64', 'int64']:
            table.append([str(i), df.columns[i]])
    print(tabulate(table, headers, tablefmt='pretty'))

    # TO DO: Need to add while loop to validate selection
    weight_col = df.columns[int(input('Please select the weight column (enter index no.): '))]
    _weight_ls = sorted(list(df[weight_col].unique()))
    _max_weight = max(_weight_ls)

    # Create random sperator for system generated UID
    _bgex = '=='

    # Create chances dictionary
    # chances are the reverse of weights, the more weights the least chance and the less weights the more chanese
    retry = 0
    while True:
        equal_chance = input(tabulate([[1, 'Equal Chance'], [2, 'Weighted Chance']], headers=['Choice', 'Chance Type'], tablefmt='pretty') + "\nSelect Choice 1 or 2: ")
        # TO DO: while loop validate input
        if equal_chance == "1":
            equal_chance = 1
            break
        elif equal_chance == "2":
            equal_chance = 0
            break
        else:
            retry += 1
            if retry > 3:
                raise ValueError(f"Chance input error after multiple retries, expected 1 or 2, given {equal_chance}")
            else:
                print("Invalid input. Please try again.")

    chances = {}
    for i in range(len(_weight_ls)):
        if equal_chance:
            chances[_weight_ls[i]] = 1
        else:
            chances[_weight_ls[i]] = _weight_ls[int(f"-{i+1}")]

    # Create ballot dataframe
    ballot_ls = []
    for uid in df[uid_col].unique():
        weight = df[df[uid_col] == uid][weight_col].values[0]
        chance = chances[weight]
        for i in range(chance):
            ballot_ls.append({'Ballot_UID': f'{uid}{_bgex}{i+1}'})

    ballot_df = pd.DataFrame(ballot_ls)
    org_ballot_df = pd.DataFrame(ballot_ls)

    print(" Configuration End ".center(DISPLAY_UNIT, "=") + "\n")

    # Draw and create Winner dataframe
    winner_df = pd.DataFrame()
    remaining_resource = total_resource

    # Print Draw list
    print(" Draw List ".center(DISPLAY_UNIT, "=") + "\n" + tabulate(df, headers="keys", tablefmt="pretty") + "\n" + "".center(DISPLAY_UNIT, '='))

    ballot = True
    print(" Draw Start ".center(DISPLAY_UNIT, "="))
    while ballot:
        time.sleep(delay)
        if remaining_resource >= _max_weight:
            # Start draw using random seed
            winner_draw = ballot_df.loc[random.randint(0, len(ballot_df) - 1), 'Ballot_UID']
            winner_uid = winner_draw.split(_bgex)[0]
            winner_weight = df[df[uid_col].astype('str') == winner_uid][weight_col].values[0]

            # Append winner to winner dataframe
            print(f"{winner_uid} has won {winner_weight} {resource_name}".center(DISPLAY_UNIT, " "))
            winner_df = winner_df.append(df[df[uid_col] == winner_uid])

            # Deduct resource
            remaining_resource -= winner_weight

            # Remove ballot with similar winner_uid from ballot dataframe
            ballot_df = ballot_df[~ballot_df['Ballot_UID'].str.contains(winner_uid)]
            ballot_df.reset_index(drop=True, inplace=True)
        else:
            ballot = False
            print(" Draw End ".center(DISPLAY_UNIT, "="))
            print(f"Out of {total_resource} {resource_name}(s), remains {remaining_resource} {resource_name}(s)")
            print("".center(DISPLAY_UNIT, "="))
            print(f" Winning Draws ".center(DISPLAY_UNIT, "="))
            print(tabulate(winner_df.set_index('Name'), headers='keys', tablefmt='pretty'))
            # Create loser dataframe
            loser_uid_ls = ballot_df['Ballot_UID'].str.split(_bgex, expand=True)[0].unique()
            loser_df = pd.DataFrame()
            for loser_uid in loser_uid_ls:
                loser_df = loser_df.append(df[df[uid_col] == loser_uid])
            print(f" No Wins ".center(DISPLAY_UNIT, "="))
            print(tabulate(loser_df.set_index('Name'), headers='keys', tablefmt='pretty'))
            break

    print("".center(DISPLAY_UNIT, "="))

    return df, org_ballot_df, winner_df, loser_df


if __name__ == "__main__":
    sys.exit(run_ballot(input_path=INPUT_FILE, total_resource=TOTAL_RESOURCE, resource_name='ticket', delay=1))
