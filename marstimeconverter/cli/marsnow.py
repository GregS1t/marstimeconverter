#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 20:30:36 2019

@author  : Greg Sainton
@purpose : Program to print the LMST date of 'now'

No argument needed
"""

from marstimeconverter.converter import MarsTimeConverter
from pathlib import Path
import os
import sys
import getopt

def main(argv):
    try:
        MARSCONVERTER = os.environ["MARSCONVERTER_SCRIPTS"]
    except KeyError:
        MARSCONVERTER = ""
    
   # Default configuration file path
    path2marsconverter = os.environ['MARSCONVERTER_SCRIPTS']
    configfile = os.path.join(path2marsconverter, "CONFIG",
                            'mission_config_file.xml')

    my_file = Path(configfile)

    try:
        opts, args = getopt.getopt(argv, "ho:", ["help", "option="])
    except getopt.GetoptError:
        print('Usage: python marsnow.py -o <option>')
        print('Use python marsnow.py -h for help')
        sys.exit(2)
    
    option = None
    for opt, arg in opts:
        if opt == '-h':
            print('python marsnow.py -o <option>\n'\
                  '     Function to get LMST now with various formats for the InSight lander.\n'
                  '       It can be easely adapted for other missions \n\n'\
                  '             @author: Greg Sainton (sainton@ipgp.fr)\n'\
                  '             @version:2.0 (Mar 25)\n\n'\
                  '      -o --option   <option> to return the sol \n'\
                  '                    if <option> = date -> return the date and time\n'\
                  '                    if <option> = sol  -> return the sol number\n'
                  '      -h This help message.')
            sys.exit()
        elif opt in ["--option", "-o"]:
            option = str(arg)
    
    if my_file.is_file():
        mDate = MarsTimeConverter(configfile)
    else:
        sys.exit("mission_config_file.xml is missing")

    marsDateNow = mDate.utc2lmst()
    posT = marsDateNow.find('T')
    
    if option is not None:
        if option.lower() == "sol":
            print(int(marsDateNow[:posT]))
        elif option.lower() == "date":
            print(marsDateNow)
    else:
        print("Today, it is", marsDateNow)
        print("SOL", marsDateNow[:posT], "from", \
              str(mDate.lmst2utc(lmst_date=int(marsDateNow[:posT]))), \
              "UTC to", str(mDate.lmst2utc(lmst_date=(int(marsDateNow[:posT]) + 1))))

if __name__ == '__main__':
    main(sys.argv[1:])
