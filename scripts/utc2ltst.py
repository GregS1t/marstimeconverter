#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tus Jan 04 15:24:10 2022

@purpose: program to convert utc DateTime format to ltst for InSight mission
@author: Gregory Sainton
@mail: sainton@ipgp.fr

"""
import sys, getopt
from datetime import datetime

	# Internal lib
from MarsConverter import MarsConverter


def main(argv):

	from pathlib import Path
	from obspy import UTCDateTime

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
	output = None
	try:
		opts, args = getopt.getopt(argv,"hd:f:",["date=", "format="])
	except getopt.GetoptError:
		print ('python utc2ltst.py -d <date>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print(\
			"python utc2ltst -d <date> -f <format>\n"\
			"       function to convert utc time to ltst time according to InSight landing parameters   \n\n"\
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
				print(mDate.get_utc_2_ltst(output=output))
			else:
				#print("output est date")
				print(mDate.get_utc_2_ltst(output="date"))
		else:
			try:
				t_utc = UTCDateTime(t_opt)
				if output == "decimal":
					#print("output est decimal")
					print(mDate.get_utc_2_ltst(utc_date=t_utc, output=output))
				else:
					#print("output est date")
					print(mDate.get_utc_2_ltst(utc_date=t_utc, output="date"))
			except:
				print("Please check the format of the date.")
	else:
		print("Input time is not defined.")

if __name__ == '__main__':
	main(sys.argv[1:])