#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 20:30:36 2019

@author  : greg
@purpose : tribial program to be executed with shell script marsnow to print
			the LMST date of 'now'

No argument needed

"""

from MarsConverter import MarsConverter
from pathlib import Path
import os, sys
import getopt



def main(argv):

	try:
		MARSCONVERTER = os.environ["MARSCONVERTER"]
	except KeyError:
		MARSCONVERTER = ""
	landerconfigfile = os.path.join(MARSCONVERTER, "landerconfig.xml")
	#landerconfigfile = MARSCONVERTER+"/"+'./landerconfig.xml'
	my_file = Path(landerconfigfile)

	try:
		opts, args = getopt.getopt(argv,"ho:",["help","option="])
	except getopt.GetoptError:
		print ('python marsnow.py -opt <option> ')
		print ('python marsnow.py -h for help')
		sys.exit(2)
	option = None
	for opt, arg in opts:
		if opt == '-h':
			print ('python marsnow.py -o <option> \n'\
					'     function to get LMST now with various formats.\n\n'\
					'             @author: Greg Sainton (sainton@ipgp.fr)\n'\
					'             @version:1.1 (jan 20)\n\n'\
					'      -o --option   <option> to return the sol \n'\
					'                    if <option> = date -> return the date and time\n'\
					'                    if <option> = sol  -> return the sol number   '\
					)
			sys.exit()
		elif opt in ["--option", "--opt", "-o"]:
			option = str(arg)
		else:
			option = None


	if my_file.is_file():
		mDate = MarsConverter(landerconfigfile)
	else:
		sys.exit("landerconfigfile is missing")

	marsDateNow = mDate.get_utc_2_lmst()
	posT = marsDateNow.find('T')
	if option is not None:
		if option.lower() == "sol":
			print(int(marsDateNow[0:posT]))
		elif option.lower() == "date":
			print(marsDateNow)
	else:
		print("Today, it is ", marsDateNow)
		print("SOL ",marsDateNow[:posT] ,"from ", \
			str(mDate.get_lmst_to_utc(lmst_date=int(marsDateNow[:posT]))), \
			" UTC to ", str(mDate.get_lmst_to_utc(lmst_date=(int(marsDateNow[:posT])+1))))

if __name__ == '__main__':
	main(sys.argv[1:])
