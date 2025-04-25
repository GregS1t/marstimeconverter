#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 04 15:24:10 2022

@purpose: Program to convert UTC DateTime format to LTST.
@author: Gregory Sainton
"""
import sys
import getopt
import os
from datetime import datetime
from pathlib import Path
from marstimeconverter.converter import MarsTimeConverter

def main(argv):
    try:
        MARSCONVERTER = os.environ["MARSCONVERTER_SCRIPTS"]
    except KeyError:
        MARSCONVERTER = ""
    
    landerconfigfile = os.path.join(MARSCONVERTER, "CONFIG", 
                                    "mission_config_file.xml")
    my_file = Path(landerconfigfile)

    if not my_file.is_file():
        sys.exit("mission_config_file.xml is missing")
    
    mDate = MarsTimeConverter(landerconfigfile)
    t_opt = None
    output = "date"
    
    try:
        opts, args = getopt.getopt(argv, "hd:f:", ["date=", "format="])
    except getopt.GetoptError:
        print('Usage: python utc2ltst.py -d <date> -f <format>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print("python utc2ltst.py -d <date> -f <format>\n"\
                  "       Function to convert UTC time to LTST time.\n\n"\
                  "     -d   date in datetime format, e.g., '2019-08-26T11:47:23.5646623'\n"\
                  "     -f   output format: 'date' or 'decimal' (default: date)")
            sys.exit()
        elif opt in ("-d", "--date"):
            t_opt = arg
        elif opt in ("-f", "--format"):
            output = arg
    
    if t_opt:
        if t_opt.lower() == "now":
            print(mDate.utc2ltst(output=output))
        else:
            try:
                t_utc = datetime.fromisoformat(t_opt)
                print(mDate.utc2ltst(utc_date=t_utc, output=output))
            except ValueError:
                print("Please check the format of the date.")
    else:
        print("Input time is not defined.")

if __name__ == '__main__':
    main(sys.argv[1:])

