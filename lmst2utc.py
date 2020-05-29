#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 12:07:56 2019

@author: Greg
"""

import sys, getopt

	# Internal lib
from MarsTimeConverter import MarsTimeConverter


def main(argv):

	from pathlib import Path
	from obspy import UTCDateTime
	from datetime import datetime


	import os
	try:
		MARSCONVERTER = os.environ["MARSCONVERTER"]
	except KeyError:
		MARSCONVERTER = ""
	
	landerconfigfile = MARSCONVERTER+"/"+'./landerconfig.xml'
	my_file = Path(landerconfigfile)

	if my_file.is_file():
		mDate = MarsTimeConverter(landerconfigfile)

	t_opt = None
	output = None
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
		#try:
		print(mDate.get_lmst_to_utc(lmst_date = t_opt))
		#except:
		#	print("Please check the format of the date.")
	else:
		print("Input time is not defined.")

if __name__ == '__main__':
	main(sys.argv[1:])