#!/usr/bin/env python

'''
This script for running Singapore Flyer Campaign.
import from simple_ballot to execute `ballot` script commands
'''
import os
from simple_ballot import ballot

df, org_ballot_df, winner_df, loser_df = ballot.run_draw(input_path=r"C:\Users\aloo\Downloads\SFT.csv", total_resource=294, delay=1)

dst = r".\output"

try:
    os.mkdir(dst)
except:
    pass

df.to_csv("SFT_data.csv", index=False)
org_ballot_df.to_csv("Draw_data.csv", index=False)
winner_df.to_csv("Winner_data.csv", index=False)
loser_df.to_csv("Loser_data.csv", index=False)
