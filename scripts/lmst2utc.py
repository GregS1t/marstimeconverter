#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 12:07:56 2019

@author: Greg
"""

import sys, getopt

    # Internal lib
from MarsConverter import MarsConverter


def main(argv):

    from pathlib import Path

    import os
    try:
        MARSCONVERTER = os.environ["MARSCONVERTER"]
    except KeyError:
        MARSCONVERTER = ""
    
    landerconfigfile = MARSCONVERTER+"/"+'./landerconfig.xml'
    my_file = Path(landerconfigfile)

    if my_file.is_file():
        mDate = MarsConverter(landerconfigfile)

    t_opt = None
    try:
        opts, args = getopt.getopt(argv,"hd:",["lmst=", "format="])
    except getopt.GetoptError:
        print ('python utc2lmst.py -d <date>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(\
            "python lmst2utc -d <date> \n"\
            "       function to convert utc time to lmst time according to InSIght landing parameters   \n\n"\
            "     -t   time with a datetime format. eg. '0265T11:47:23:5646623'\n")
            sys.exit()
        elif opt in ("-d", "--date"):
            t_opt = arg
            #print(t_opt)


    if t_opt is not None:
        try:
            print(mDate.get_lmst_to_utc(lmst_date = t_opt))
        except:
            print("LMST2UTC: Please check the format of the date. We are expecting a sol number")
    else:
        print("LMST2UTC: Input time is not defined.")

if __name__ == '__main__':
    main(sys.argv[1:])
