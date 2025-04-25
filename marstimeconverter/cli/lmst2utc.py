#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 12:07:56 2019

@author: Greg
"""
import sys
import getopt
import os
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
    
    try:
        opts, args = getopt.getopt(argv, "hd:", ["lmst="])
    except getopt.GetoptError:
        print('Usage: python lmst2utc.py -d <LMST time>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print("python lmst2utc.py -d <LMST time>\n"\
                  "       Function to convert LMST time to UTC.\n\n"\
                  "     -d   time in LMST format, e.g., '0265T11:47:23:5646623'")
            sys.exit()
        elif opt in ("-d", "--lmst"):
            t_opt = arg
    
    if t_opt:
        try:
            print(mDate.lmst2utc(lmst_date=t_opt))
        except Exception:
            print("LMST2UTC: Please check the format of the LMST date.")
    else:
        print("LMST2UTC: Input time is not defined.")

if __name__ == '__main__':
    main(sys.argv[1:])

