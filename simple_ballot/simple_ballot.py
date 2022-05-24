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


class System:

    def __init__(self, io=None):
        try:
            self.add_data(io)
        except IOError:
            pass

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
        transform supported data type to pandas.DataFrame
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
        '''
        Creates logger for record
        Creates a log handler and transcipt handler for later export
        '''
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        file_formatter = logging.Formatter('%(asctime)s\t[%(funcName)s][%(levelname)s]:\t%(message)s')
        self.log_io = io.StringIO()
        log_handler = logging.StreamHandler(self.log_io)
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(file_formatter)

        transcript_formatter = logging.Formatter('%(message)s')
        self.transcript_io = io.StringIO()
        transcript_handler = logging.StreamHandler(self.transcript_io)
        transcript_handler.setLevel(logging.DEBUG)
        transcript_handler.setFormatter(transcript_formatter)

        self.logger.addHandler(log_handler)
        self.logger.addHandler(transcript_handler)

    def _add_log_stream(self):
        '''
        Adds log streamer
        '''
        stream_formatter = logging.Formatter('t%(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(stream_formatter)
        self.logger.addHandler(stream_handler)

    def ballot(self):
        '''
        Ballot function:
        '''
        print(f"call [{self.io}] ballot")

    def draw(
        self,
        resource=None,
        resource_name='',
        unique_column='auto',
        show_console=True,
        export_transcript=False,
        transcript_filename="draw_transcript.txt",
        export_log=False,
        log_filename="draw_logs.txt",
        delay=1
    ):
        '''
        Function to perform lucky draw

        Parameters:
            resource (int): an integer value of the total available resources for the draw, default is None.

            resource_name (str): the name of the resource, eg: ticket, voucher, etc, default is "".

            unique_column (str/list): if set "auto" system will auto seach columns with number of unique values equals to total length of values. If none found, will raise error. If set to specific named column, user requires to input list of names in a list instance. If more than one name is indicated a combination of these columns will be done to create new column, else will just use the only named column. Default is "auto"

            show_console (bool): if set to True will displace transcript in console, default is False

            export_transcript (bool): if set to True will export transcript to defined path in transcript_filename, default is False

            transcript_filename (str/path): the absolute path for exported transcript. Default is "draw_transcript.txt"

            export_log (bool): if set to True will export transcript to defined path in log_filename, default is False

            log_filename (str/path): the absolute path for exported logs. Default is "draw_logs.txt"

        '''
        unique_column_kw = ['auto']

        if self.io is None:
            raise IOError("Require an input data to proceed - no data or file path provided.")

        self._create_logger()

        if show_console:
            self._add_log_stream()  # Add streamer

        if resource is None:
            raise ValueError("Expected integer more than 0, given None")

        self.logger.info(" Configuration Start ".center(DISPLAY_UNIT, '='))

        df = self.io
        # Check for duplicate
        if any(df.duplicated()):
            self.logger.warning(f"Dropping duplicates:\n{tabulate(df[df.duplicated()], tablefmt='pretty')}")
            df.drop_duplicates(inplace=True)
            df.reset_index(drop=True, inplace=True)

        # find unique id column
        uid_col = None

        # Checks for unique identity column
        if isinstance(unique_column, str):
            if unique_column.lower() == 'auto':
                # Check for unique identity column and try to auto create one
                df['UID'] = ['-'.join(i) for i in zip(*[df[s].map(str) for s in df.columns])]
                if df['UID'].nunique() == len(df):
                    uid_col = 'UID'
                    self.logger.info(f"Auto generate [{uid_col}] column.")
                else:
                    raise ValueError(f"Unable to create unique column, length of unique column and length of data is the same - {len(df)}")
            else:
                raise ValueError(f"Expected unique_column key word to be either {', '.join(unique_column_kw)}, given {unique_column}")

        elif isinstance(unique_column, list):
            if all([col in df.columns for col in unique_column]):
                if len(unique_column) == 1:
                    df['UID'] = df[unique_column[0]]
                elif len(unique_column) > 1 and len(unique_column) <= len(df.columns):
                    df['UID'] = ['-'.join(i) for i in zip(*[df[s].map(str) for s in unique_column])]
                else:
                    raise ValidationError(f"The number of items listed in unique_column does not match the requirement of existing column in dataframe - {'No items listed' if len(unique_column) == 0 else 'Too many items listed'}")

                if df['UID'].nunique() == len(df['UID']):
                    uid_col = 'UID'
                else:
                    raise ValueError(f"Unable to create a column with unique values. Check given column names - {unique_column}")
            else:
                raise ValueError(f"Some column not found, available columns {df.columns}, given {unique_column}")

        else:
            raise ValidationError(f"unique_column attribute accepts either string instance or list instance, given {type(unique_column)} instance")

        # Create ballot dataframe
        # Assuming all equal chance
        ballot_ls = []
        for uid in df[uid_col].unique():
            ballot_ls.append({'Ballot_UID': uid})
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
                self.logger.info(f"Out of {resource} {resource_name}(s), remains {remaining_resource} {resource_name}(s)")
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
