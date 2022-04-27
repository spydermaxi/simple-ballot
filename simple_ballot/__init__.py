# -*- coding: utf-8 -*-

"""Simple system for automatic ballot/draw"""

from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import time
import random
import logging

from tabulate import tabulate
import pandas as pd

if sys.version_info[0] < 3:

    def _is_file(f):
        return hasattr(f, "read")

else:

    import io

    def _is_file(f):
        return isinstance(f, io.IOBase)

__version__ = '0.0.1'
__author__ = 'Adrian Loo'
__all__ = ['System']


# Constants
BOOL = ['y', 1, 't', 'yes', 'true', '', ' ']
DISPLAY_UNIT = 60


class SB_System:

    def __init__(self):
        self.io = None

    def add_data(self, io):
        self.io = io
        if self.io is None or "":
            raise IOError("No data or file path provided. Try adding data using .add_data()")
        elif os.path.isfile(self.io):
            self.io = pd.read_csv(self.io)
        else:
            self.io = self._normalize_data(self.io)

    def _normalize_data(self, data):
        '''
        transform supported datat type to pandas.DataFrame
        '''

        if hasattr(data, "keys") and hasattr(data, "values"):
            # This is a pandas.DataFrame or a dictionary
            if hasattr(data, "index"):
                # This is likely a pandas.DataFrame
                return data
            elif hasattr(data.values, "__call__") and all([isinstance(v, list) for v in data.values()]):
                # likely a conventional dict
                return pd.DataFrame(data)
            else:
                raise ValueError("io data doesn't appear to be a dict or a pandas.DataFrame")
        else:
            # should be any iterable accepted by pandas.DataFrame
            return pd.DataFrame(data)

    def _create_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        file_formatter = logging.Formatter('%(asctime)s\t[%(funcName)s][%(levelname)s]:\t%(message)s')
        self.log_io = io.StringIO()
        log_handler = logging.StreamHandler(self.log_io)
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(file_formatter)

        transcript_formatter = logging.Formatter('t%(message)s')
        self.transcript_io = io.StringIO()
        transcript_handler = logging.StreamHandler(self.transcript_io)
        transcript_handler.setLevel(logging.DEBUG)
        transcript_handler.setFormatter(transcript_formatter)

        self.logger.addHandler(log_handler)
        self.logger.addHandler(transcript_handler)

    def _add_log_stream(self):
        stream_formatter = logging.Formatter('t%(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(stream_formatter)
        self.logger.addHandler(stream_handler)

    def ballot(self):
        print(f"call [{self.io}] ballot")

    def draw(self, resource=None, resource_name='', delay=1, show_console=True, export_transcript=False, transcript_filename=None, export_log=False, log_filename=None):

        if self.io is None:
            raise IOError("Require an input data to proceed - no data of file path provided.")

        self.logger = self._logger()

        if show_console:
            self._add_log_stream()  # Add streamer

        if resource is None:
            raise ValueError("Expected integer more than 0, given None")

        self.logger.info(" Configuration Start ".center(DISPLAY_UNIT, '='))

        df = self.io
        # Check for duplicate
        if any(df.duplicated()):
            self.logger.warning(f"Duplicates found:\n{tabulate(df[df.duplicated()], tablefmt='pretty')}\nDropping duplicates")
            df.drop_duplicates(inplace=True)
            df.reset_index(drop=True, inplace=True)

        # find unique id column
        uid_col = None

        # Checks for unique identity column
        self.logger.info("Checking Columns for unique data")
        for col in df.columns:
            if df[col].nunique() == len(df):
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
                self.logger.info(f"Auto generate [{uid_col}] column.")
            else:
                raise ValueError("No unique column can be created")

        # ask for weight column
        headers = ['Index', 'Column Name']
        table = []
        for i in range(len(df.columns)):
            if df.dtypes[df.columns[i]].name in ['float64', 'int64']:
                table.append([str(i), df.columns[i]])
        self.logger.info(tabulate(table, headers, tablefmt='pretty'))

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
                    self.logger.info("Invalid input. Please try again.")

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

        self.logger.info(" Configuration End ".center(DISPLAY_UNIT, "=") + "\n")

        # Draw and create Winner dataframe
        winner_df = pd.DataFrame()
        remaining_resource = resource

        # Print Draw list
        self.logger.info(" Draw List ".center(DISPLAY_UNIT, "=") + "\n" + tabulate(df, headers="keys", tablefmt="pretty") + "\n" + "".center(DISPLAY_UNIT, '='))

        ballot = True
        self.logger.info(" Draw Start ".center(DISPLAY_UNIT, "="))
        while ballot:
            time.sleep(delay)
            if remaining_resource >= _max_weight:
                # Start draw using random seed
                winner_draw = ballot_df.loc[random.randint(0, len(ballot_df) - 1), 'Ballot_UID']
                winner_uid = winner_draw.split(_bgex)[0]
                winner_weight = df[df[uid_col].astype('str') == winner_uid][weight_col].values[0]

                # Append winner to winner dataframe
                self.logger.info(f"{winner_uid} has won {winner_weight} {resource_name}".center(DISPLAY_UNIT, " "))
                winner_df = winner_df.append(df[df[uid_col] == winner_uid])

                # Deduct resource
                remaining_resource -= winner_weight

                # Remove ballot with similar winner_uid from ballot dataframe
                ballot_df = ballot_df[~ballot_df['Ballot_UID'].str.contains(winner_uid)]
                ballot_df.reset_index(drop=True, inplace=True)
            else:
                ballot = False
                self.logger.info(" Draw End ".center(DISPLAY_UNIT, "="))
                self.logger.info(f"Out of {total_resource} {resource_name}(s), remains {remaining_resource} {resource_name}(s)")
                self.logger.info("".center(DISPLAY_UNIT, "="))
                self.logger.info(f" Winning Draws ".center(DISPLAY_UNIT, "="))
                self.logger.info(tabulate(winner_df.set_index('Name'), headers='keys', tablefmt='pretty'))
                # Create loser dataframe
                loser_uid_ls = ballot_df['Ballot_UID'].str.split(_bgex, expand=True)[0].unique()
                loser_df = pd.DataFrame()
                for loser_uid in loser_uid_ls:
                    loser_df = loser_df.append(df[df[uid_col] == loser_uid])
                self.logger.info(f" No Wins ".center(DISPLAY_UNIT, "="))
                self.logger.info(tabulate(loser_df.set_index('Name'), headers='keys', tablefmt='pretty'))
                break

        self.logger.info("".center(DISPLAY_UNIT, "="))

        if export_transcript and transcript_filename is not None:
            with open(transcript_filename, 'w') as fw:
                fw.writelines(self.transcript_io.getvalue())

        if export_log and log_filename is not None:
            with open(log_filename, 'w') as fw:
                fw.writelines(self.log_io.getvalue())

        if self.logger:
            del self.logger
            del self.transcript_io
            del self.log_io
