# encoding: utf8

import time
import sys
import random
import pandas as pd

__version__ = '0.0.1'


# Constants
INPUT_FILE = r"..\test\applicants.csv"
TOTAL_RESOURCE = 30
DISPLAY_UNIT = 60  # Letter Space


def run_ballot(input_path=None, total_resource=None, resource_name='ticket', delay=1):
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
    print("Configuration Start".center(DISPLAY_UNIT, '='))

    # Check for duplicate
    if any(df.duplicated()):
        print("Duplicate Data".center(DISPLAY_UNIT, '='))
        print(df[df.duplicated()])
        print("Duplicate index found, proceed to drop duplicates")
        df.drop_duplicates(inplace=True)

    # find unique id column
    uid_col = None

    # Checks for unique identity column
    print("".center(DISPLAY_UNIT, '='))
    print("Checking Columns for unique identities")
    for col in df.columns:
        if df[col].nunique() == len(df):
            uid_col = col
            confirm = input(f"Found unique column - {col}, Use this?[Y/n] ")
            if confirm == "" or 'y' in confirm.lower():
                df[uid_col] = df[uid_col].astype('str')
                break
            else:
                uid_col = None

    # Validate auto find
    if uid_col is None:
        print("".center(DISPLAY_UNIT, '='))
        print("No unique identity column defined/detected.", end=" ")
        # Check for unique identity column and try to auto create one
        df['UID'] = ['-'.join(i) for i in zip(*[df[s].map(str) for s in df.columns])]
        if df['UID'].nunique() == len(df):
            uid_col = 'UID'
            print(f"Generated [{uid_col}] column.")
        else:
            raise ValueError("No unique column can be created")

    # ask for weight column
    print("List of columns in your dataframe".center(DISPLAY_UNIT, '='))
    print("| Index".ljust(8, " ") + "| Column Name".ljust(max([len(s) for s in df.columns]) + 3, " ") + "|")
    for i in range(len(df.columns)):
        print(f"| {i}".ljust(8, " ") + f"| {df.columns[i]}".ljust(max([len(s) for s in df.columns]) + 3, " ") + "|")
    # TO DO: Need to add while loop to validate selection
    weight_col = df.columns[int(input('Please select the weight column (enter index no.): '))]
    _weight_ls = sorted(list(df[weight_col].unique()))
    _max_weight = max(_weight_ls)
    print("Configuration End".center(DISPLAY_UNIT, "=") + "\n")

    # Create random sperator for system generated UID
    _bgex = '=='

    # Create chances dictionary
    # chances are the reverse of weights, the more weights the least chance and the less weights the more chanese
    equal_chance = input("Select 1.Equal Chance or 2.Weighted Chance: ")
    # TO DO: while loop validate input
    if equal_chance == "1":
        equal_chance = 1
    elif equal_chance == "2":
        equal_chance = 0
    else:
        raise ValueError("Invalid input. Please try again.")

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

    # Draw and create Winner dataframe
    winner_df = pd.DataFrame()
    remaining_resource = total_resource

    ballot = True
    print("Draw Starts".center(DISPLAY_UNIT, "="))
    while ballot:
        time.sleep(delay)
        if remaining_resource >= _max_weight:
            # Start draw using random seed
            winner_draw = ballot_df.loc[random.randint(0, len(ballot_df) - 1), 'Ballot_UID']
            winner_uid = winner_draw.split(_bgex)[0]
            winner_weight = df[df[uid_col].astype('str') == winner_uid][weight_col].values[0]

            # Append winner to winner dataframe
            print(f"{winner_uid} has won {winner_weight} {resource_name}")
            winner_df = winner_df.append(df[df[uid_col] == winner_uid])

            # Deduct resource
            remaining_resource -= winner_weight

            # Remove ballot with similar winner_uid from ballot dataframe
            ballot_df = ballot_df[~ballot_df['Ballot_UID'].str.contains(winner_uid)]
            ballot_df.reset_index(drop=True, inplace=True)

        else:
            ballot = False
            print("Draw Ended".center(DISPLAY_UNIT, "="))
            print(f"Out of {total_resource} {resource_name}(s), remains {remaining_resource} {resource_name}(s)")
            print("".center(DISPLAY_UNIT, "="))
            print(f"Winning Participants".center(DISPLAY_UNIT, "="))
            print(winner_df)
            # Create loser dataframe
            loser_uid_ls = ballot_df['Ballot_UID'].str.split(_bgex, expand=True)[0].unique()
            loser_df = pd.DataFrame()
            for loser_uid in loser_uid_ls:
                loser_df = loser_df.append(df[df[uid_col] == loser_uid])
            print(f"Remaining Participants".center(DISPLAY_UNIT, "="))
            print(loser_df)
            break

    print("".center(DISPLAY_UNIT, "="))

    return df, org_ballot_df, winner_df, loser_df


if __name__ == "__main__":
    sys.exit(run_ballot(input_path=INPUT_FILE, total_resource=TOTAL_RESOURCE, resource_name='ticket', delay=1))
