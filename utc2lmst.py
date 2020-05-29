#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 11:11:10 2019

@author: Greg
"""
import sys, getopt
from datetime import datetime

	# Internal lib
from MarsTimeConverter import MarsTimeConverter


def main(argv):

	from pathlib import Path
	from obspy import UTCDateTime
	from datetime import datetime


	from pathlib import Path
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
		opts, args = getopt.getopt(argv,"hd:f:",["date=", "format="])
	except getopt.GetoptError:
		print ('python utc2lmst.py -d <date>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print(\
			"python utc2lmst -d <date> -f <format>\n"\
			"       function to convert utc time to lmst time according to InSIght landing parameters   \n\n"\
			"     -d   date with a datetime format. eg. '2019-08-26T11:47:23.5646623'\n"\
			"     -f   output format : 'date' or 'decimal' (date by default)")
			sys.exit()
		elif opt in ("-d", "--date"):
			t_opt = arg
		elif opt in ("-f", "--format"):
			output = arg

	if t_opt is not None:
		if t_opt == "now":
			if output == "decimal":
				#print("output est decimal")
				print(mDate.get_utc_2_lmst(output=output))
			else:
				#print("output est date")
				print(mDate.get_utc_2_lmst(output = "date"))
		else:
			try:
				t_utc = UTCDateTime(t_opt)
				if output == "decimal":
					#print("output est decimal")
					print(mDate.get_utc_2_lmst(utc_date = t_utc, output=output))
				else:
					#print("output est date")
					print(mDate.get_utc_2_lmst(utc_date = t_utc, output = "date"))
			except:
				print("Please check the format of the date.")
	else:
		print("Input time is not defined.")

if __name__ == '__main__':
	main(sys.argv[1:])