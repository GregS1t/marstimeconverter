#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  
	@date: December 2018, 7th
	@author: sainton@ipgp.fr - Greg Sainton @IPGP on Behalf InSight/SEIS collaboration 
	@purpose: 
		This module is a class "Mars Time Converter" designed to convert UTC Time to LMST 
		Time and LMST Time to UTC Time
  
		LMST Time is depending on the landing time and the longitude of the lander. 
		Those informations are provided in a configuration file named "landerconfig.xml"
		
		All the calculation are based of the Mars 24 algorithm itself based on
		Alison, McEwen, Planetary ans Space Science 48 (2000) 215-235
		https://www.giss.nasa.gov/tools/mars24/help/algorithm.html
		
		Beware that mumerical values and leap seconds were updated in this algo
		since the publication of the article. 
		
		I followed this :https://www.giss.nasa.gov/tools/mars24/help/algorithm.html
		In comments, AM2000 refers to the article and C? refers to the above web
		page.
		
		

	@VERSIONS:
		V.1.5: Dec 2019 - Add local solar elevation 
							+ latitude added in lander configfile
		
		V.1.4: Dec 2019 - Add Solar declination and LTST getter
		
		V1.3: Oct 2019 - Update in the output format of the utc2lmst functions: 
			 no more colons between seconds and milliseconds

		V1.0: April 2019 - LMST -> UTC added.
			It was necessery to change some other function to bypass the effect 
				of modulos
			You can either give a SSSSThh:mm:ss:millis (ie 0129T02:45:56:675678) 
				of just a sol number

		# Content of landerconfigfile.xml for INSIGHT
				<configlanding>
				        <landingdate>2018-330T19:44:52.444</landingdate>
				        <longitude>224.03</longitude>
						<latitude>4.502384</latitude>
				        <solorigin>2018-330T05:10:50.3356</solorigin>
						
				</configlanding>
"""

import os
import math
from math import floor
import time
import numpy as np
from obspy import UTCDateTime


global configfile

configfile = './landerconfig.xml'
path2marstimeconverter = os.environ['MARSCONVERTER']
configfile = path2marstimeconverter+'/landerconfig.xml'

class MarsTimeConverter:
	"""
	Class which contains all the function to convert UTC time to Martian Time.
	All the calculation are based of the Mars 24 algorithm itself based on
	Alison, McEwen, Planetary ans Space Science 48 (2000) 215-235
	https://www.giss.nasa.gov/tools/mars24/help/algorithm.html
	"""


	#JULIAN UNIX EPOCH (01/01/1970-00:00 UTC)
	JULIAN_UNIX_EPOCH = 2440587.5

	#MILLISECONDS IN A DAY
	MILLISECONDS_IN_A_DAY = 86400000.0

	#SECOND IN A DAY
	SECOND_IN_A_DAY = 86400.0

	# SHIFT IN DAY PER DEGREE
	SHIFT_IN_DAY_PER_DEGREE = 1. / 360.0

	# Julian day of reference (january 2010, 6th 00:00 UTC) At that time, 
	# the martian meridian is also at midnight.
	CONSISTENT_JULIAN_DAY = 2451545.0

	#Delta between IAT and UTC
	TAI_UTC = 0.0003725
	#time division
	TIME_COEFFICIENT = 60.0

	#Millisecond multiplier
	MMULTIPLIER = 1000.0

	# Allison's coefficient
	K = 0.0009626

	# Allison's normalisation factor to make sure that we get positive values 
	#for date after 1873
	KNORM = 44796.0

	#Ratio Betwwen Martian SOL and terrestrial day
	SOL_RATIO = 1.0274912517

	LONGITUDE = None

	# Sol-001 and Sol-002 start times to compute one Martian day in seconds.
	# Cannot use landing time because Sol-000 lasted shorter.
	SOL01_START_TIME = UTCDateTime("2018-11-27T05:50:25.580014Z")
	SOL02_START_TIME = UTCDateTime("2018-11-28T06:30:00.823990Z")
	
	SECONDS_PER_MARS_DAY = SOL02_START_TIME - SOL01_START_TIME - 0.000005
	


	#def __init__(self, landingdate, origindate, longitude):
	#	self.__landingdate = landingdate
	#	self.__longitude = float(longitude)
	#	self.__origindate = origindate
	#	self.LONGITUDE = float(self.__longitude)


	def __init__(self, landerconfigfile=None):
		
		global configfile
		from lxml import etree
		#import os
		
		#print("configfile: ", configfile)
		#print("Current directory: ", os.getcwd())
		
		if landerconfigfile is not None:
			configfile = configfile
			#print("Il est pas none")
		else:
			#print("il est none" )
			configfile = configfile
		
		#print("configfile: ", configfile)
		#print("Current directory: ", os.getcwd())
		
		tree = etree.parse(configfile)
		root = tree.getroot()
		for el in root:
			if el.tag == 'landingdate':
				LANDING_DATE_STR = el.text
			if el.tag == 'longitude':
				LANDING_LONGITUDE = float(el.text)
			if el.tag == 'solorigin':
				SOL_ORIGIN_STR = el.text
			if el.tag == 'latitude':
				LANDING_LATITUDE = float(el.text)
			
		utc_origin_sol_date = UTCDateTime(SOL_ORIGIN_STR)
		utc_landing_date = UTCDateTime(LANDING_DATE_STR)

		self.__landingdate =  utc_landing_date
		self.__longitude = LANDING_LONGITUDE
		self.__origindate = utc_origin_sol_date
		self.LONGITUDE = float(self.__longitude)
		self.LATITUDE  = LANDING_LATITUDE


	def get_landing_date(self):
		"""
		Returns the landing date of the lander in UTCDateTime format
		"""
		return self.__landingdate


	def get_longitude(self):
		"""
		Returns the lander longitude
		"""
		return self.__longitude


	def get_origindate(self):
		return self.__origindate


	def j2000_epoch(self):
		"""
		Returns the j2000 epoch as a float
		"""
		return self.CONSISTENT_JULIAN_DAY


	def mills(self):
		"""
		Returns the current time in milliseconds since Jan 1 1970
		"""
		return time.time()*self.MMULTIPLIER


	def julian(self, date=None):
		"""
		Returns the julian day number given milliseconds since Jan 1 1970
		"""
		if date is None:
			dateUTC = UTCDateTime.now()
		else:
				dateUTC = UTCDateTime(date)
				millis = dateUTC.timestamp * 1000.0

		return self.JULIAN_UNIX_EPOCH + (millis/self.MILLISECONDS_IN_A_DAY)


	def utc_to_tt_offset(self, jday=None):
		"""
		Returns the offset in seconds from a julian date in Terrestrial Time (TT)
		to a Julian day in Coordinated Universal Time (UTC)
		"""
		return self.utc_to_tt_offset_math(jday)


	def utc_to_tt_offset_math(self, jday=None):
		"""
		Returns the offset in seconds from a julian date in Terrestrial Time (TT)
		to a Julian day in Coordinated Universal Time (UTC)
		"""
		if jday is None:
			jday_np=self.julian()
		else:
			jday_np = jday

		jday_min = 2441317.5
		jday_vals = [	 -2441317.5, 0.,182.,366., 731., 1096., 1461., 1827., 
						2192., 2557., 2922., 3469., 3834., 4199., 4930., 5844.,
						6575., 6940., 7487., 7852.,8217., 8766., 9313., 9862.,
						 12419., 13515., 14792., 15887., 16437.]

		offset_min = 32.184
		offset_vals = [-32.184,10., 11.0, 12.0, 13.0,
						14.0, 15.0, 16.0, 17.0, 18.0,
						19.0, 20.0, 21.0, 22.0, 23.0,
						24.0, 25.0, 26.0, 27.0, 28.0,
						29.0, 30.0, 31.0, 32.0, 33.0,
						34.0, 35.0, 36.0, 37.0]

		if jday_np <= jday_min+jday_vals[0]:
			
			return offset_min+offset_vals[0]
		elif jday_np >= jday_min+jday_vals[-1]:
			
			return offset_min+offset_vals[-1]
		else:
			for i in range(0, len(offset_vals)):
				if (jday_min+jday_vals[i] <= jday_np) and \
						(jday_min+jday_vals[i+1] > jday_np) :
					break
			
			return offset_min+offset_vals[i]

	def julian_tt(self, jday_utc=None):
		"""
		Returns the TT Julian Day given a UTC Julian day
		"""
		if jday_utc is None:
			jday_utc = self.julian()

		jdtt = jday_utc + self.utc_to_tt_offset(jday_utc)/86400.
		#print("jdtt= ", jdtt)
		return jdtt


	def j2000_offset_tt(self, jday_tt=None):
		"""
		Returns the julian day offset since the J2000 epoch
		(AM2000, eq. 15)
		"""
		if jday_tt is None:
			jday_tt = self.julian_tt()
		return (jday_tt - self.j2000_epoch())


	def Mars_Mean_Anomaly(self, j2000_ott=None):
		"""
		Calculates the Mars Mean Anomaly for a givent J2000 julien day offset
		(AM2000, eq. 16)
		"""
		if j2000_ott is None:
			j2000_ott = self.j2000_offset_tt()
		M = 19.3871 + 0.52402073 * j2000_ott
		return M % 360.

	def Alpha_FMS(self, j2000_ott=None):
		"""
		Returns the Fictional Mean Sun angle
		(AM2000, eq. 17)
		"""
		if j2000_ott is None:
			j2000_ott = self.j2000_offset_tt()

		alpha_fms = 270.3871 + 0.524038496 * j2000_ott

		return alpha_fms % 360.


	def alpha_perturbs(self, j2000_ott=None):
		"""
		Returns the perturbations to apply to the FMS Angle from orbital 
		perturbations.
		(AM2000, eq. 18)
		"""
		if j2000_ott is None:
			j2000_ott = self.j2000_offset_tt()

		array_A   = [0.0071, 0.0057, 0.0039, 0.0037, 0.0021, 0.0020, 0.0018]
		array_tau = [2.2353, 2.7543, 1.1177, 15.7866, 2.1354, 2.4694, 32.8493]
		array_phi = [49.409, 168.173, 191.837, 21.736, 15.704, 95.528, 49.095]

		pbs = 0
		for (A, tau, phi) in zip(array_A, array_tau, array_phi):
			pbs+=A*np.cos(((0.985626 * j2000_ott/tau) + phi)*np.pi/180.)
		return pbs


	def equation_of_center(self, j2000_ott=None):
		"""
		The true anomaly (v) - the Mean anomaly (M)
		(Bracketed term in AM2000, eqs. 19 and 20)
		
		----
		INPUT
			@j2000_ott: float - offseted terrestrial time relative to j2000
		----
		OUTPUT
			@return: EOC
		"""
		if j2000_ott is None:
			j2000_ott = self.j2000_offset_tt()

		M = self.Mars_Mean_Anomaly(j2000_ott)*np.pi/180.
		pbs = self.alpha_perturbs(j2000_ott)

		EOC = (10.691 + 3.0e-7 * j2000_ott)*np.sin(M)\
			+ 0.6230 * np.sin(2*M)\
			+ 0.0500 * np.sin(3*M)\
			+ 0.0050 * np.sin(4*M)\
			+ 0.0005 * np.sin(5*M) \
			+ pbs

		return EOC



	def L_s(self, j2000_ott=None):
		"""
		Returns the Areocentric solar longitude (aka Ls)
		(AM2000, eq. 19)
		"""
		
		if j2000_ott is None:
			j2000_ott = self.j2000_offset_tt()

		alpha = self.Alpha_FMS(j2000_ott)
		v_m   = self.equation_of_center(j2000_ott)

		ls = (alpha + v_m)
		ls = ls % 360
		return ls


	def equation_of_time(self, j2000_ott=None):
		"""
		Equation of Time, to convert between Local Mean Solar Time
		and Local True Solar Time, and make pretty analemma plots
		(AM2000, eq. 20)
		
		
		"""
		if j2000_ott is None:
			j2000_ott = self.j2000_offset_tt()

		ls = self.L_s(j2000_ott)*np.pi/180.

		EOT = 2.861*np.sin(2*ls)\
			- 0.071 * np.sin(4*ls)\
			+ 0.002 * np.sin(6*ls) - self.equation_of_center(j2000_ott)

		return EOT


	def j2000_from_Mars_Solar_Date(self, msd=0):
		"""
		Returns j2000 based on MSD
		"""
		j2000_ott = ((msd + 0.00096 - 44796.0) * 1.027491252) + 4.5
		return j2000_ott


	def j2000_ott_from_Mars_Solar_Date(self, msd=0):
		"""
		Returns j2000 offset based on MSD

		"""
		j2000 = self.j2000_from_Mars_Solar_Date(msd)
		j2000_ott = self.julian_tt(j2000+self.j2000_epoch())
		return j2000_ott-self.j2000_epoch()


	def Mars_Solar_Date(self, j2000_ott = None):
		"""Return the Mars Solar date"""
		if j2000_ott is None:
			jday_tt = self.julian_tt()
			j2000_ott = self.j2000_offset_tt(jday_tt)
		const = 4.5
		MSD = (((j2000_ott - const)/self.SOL_RATIO) + self.KNORM - self.K)
		return MSD


	def Coordinated_Mars_Time(self, j2000_ott = None):
		"""
		The Mean Solar Time at the Prime Meridian
		(AM2000, eq. 22, modified)
		
		Be aware that the correct version of MTC should be 
		MTC%24 but since we need to reverse the equations to go from lmst to
		utc, we decided to apply the modulo, later.
		
		"""
		if j2000_ott is None:
			jday_tt = self.julian_tt()
			j2000_ott = self.j2000_offset_tt(jday_tt)

		#print("j2000_ott: ", j2000_ott)
		MTC = 24 * (((j2000_ott - 4.5)/self.SOL_RATIO) + self.KNORM - self.K)
		return MTC


	def j2000_tt_from_CMT(self, MTC=None):
		"""
		Estimate j2000_ott from Coordinated Mars Time
		from (AM2000, eq. 22, modified)
		"""
		j2000_ott = (((MTC / 24.) + self.K - self.KNORM) *  self.SOL_RATIO) + 4.5
		return j2000_ott


	def _LMST(self, longitude=0, j2000_ott=None):
		"""
		The Local Mean Solar Time given a planetographic longitude

		19-03-12 : modif: the modulo 24 of MTC is estimated here
		(C-3)
		"""
		if j2000_ott is None:
			jday_tt = self.julian_tt()
			j2000_ott = self.j2000_offset_tt(jday_tt)
		MTC = self.Coordinated_Mars_Time(j2000_ott)
		#print("In function _LMST -> MTC: {}".format(MTC))
		MTCmod = MTC % 24
		LMST = (MTCmod - longitude * (24./360.)) % 24
		#print("In function _LMST -> LMST: {}".format(LMST))
		return LMST



	def LMST_to_j2000_ott(self, longitude=0, LMST=None):

		MTC = LMST + 24/360*longitude
		j2000_ott = self.j2000_ott_from_CMT(MTC)
		return j2000_ott


	def _LTST(self, longitude=0, j2000_ott=None):
		"""
		Local true solar time is the Mean solar time + equation of time perturbation
		from (AM2000, Eq. 23 & Eq. 24)

		"""
		if j2000_ott is None:
			jday_tt = self.julian_tt()
			j2000_ott = self.j2000_offset_tt(jday_tt)

		eot = self.equation_of_time(j2000_ott)
		lmst = self._LMST(longitude, j2000_ott)
		ltst = (lmst + eot*(1./15.))%24
		return ltst
	
	#--------------------------------------------------------------------------
	#     LTST : Local True Solar Time
	
	def get_utc_2_ltst(self, utc_date=None):
		"""
		Convert UTC date to LTST date.
		----
		INPUT:
			@utc_date: UTCDateTime
		
		----
		OUTPUT:
			@lmst_date : str 
		
		"""
		if utc_date==None:
			utc_date = UTCDateTime().now()

		if isinstance(utc_date, UTCDateTime):
			jd_utc = self.utcDateTime_to_jdutc(utc_date)
			#print("jd_utc: ", jd_utc)
		elif isinstance(utc_date, str):
			try:
				utc_date_in_utc = UTCDateTime(utc_date)
				utc_date = utc_date_in_utc
			except TypeError:
				return None
			else:
				jd_utc = self.utcDateTime_to_jdutc(utc_date_in_utc)

		jd_tt = self.julian_tt(jday_utc=jd_utc)
		jd_ott = self.j2000_offset_tt(jd_tt)
		
		origin_in_sec = self.__origindate.timestamp
		any_date_in_sec = utc_date.timestamp

		delta_sec = any_date_in_sec - origin_in_sec
		martianSol = int(delta_sec / (self.SECOND_IN_A_DAY*self.SOL_RATIO))
		
		ltst_date = self._LMST(longitude=self.__longitude, j2000_ott=jd_ott)
		
		ihour = floor(ltst_date)
		minutes = (ltst_date - ihour)*60.
		iminutes = floor(minutes)
		seconds = (minutes - iminutes)*60.
		iseconds = floor(seconds)
		milliseconds = int(math.modf((seconds-iseconds)*1000)[1])
	
		ltst_str = "{:04}T{:02}:{:02}:{:02}.{:06}".format(martianSol,ihour,\
							iminutes, iseconds, milliseconds)
	
		
		return ltst_str
		
		
		

	def utcDateTime_to_jdutc(self, date=None):
		"""
		Function to convert UTCDateTime to Julian date
		
		"""
		if date == None:
			date = UTCDateTime().now()

		millis = date.timestamp * 1000.0
		#print("millis: ", millis)
		jd_utc = self.JULIAN_UNIX_EPOCH + (float(millis) / self.MILLISECONDS_IN_A_DAY)
		#print("In utcDateTime_to_jdutc :", jd_utc )
		return jd_utc


	def jdutc_to_UTCDateTime(self, jd_utc=None):
		"""
		Function to convert Julien date to UTCDateTime
		"""

		millis = (jd_utc - self.JULIAN_UNIX_EPOCH) * self.MILLISECONDS_IN_A_DAY
		utc_tstamp = millis/1000.
		return UTCDateTime(utc_tstamp)


	def get_utc_2_lmst(self, utc_date=None, output="date"):
		"""
		Convert UTC date to LMST date. 
		Output is formated with SSSSTHH:MM:ss.mmmmmmm if output is 'date'
		Otherwise, the output is float number if output is 'decimal'
		----
		INPUT:
			@utc_date: UTCDateTime
			@output= output format which can takes those values : "date" or "decimal"
		----
		OUTPUT:
			@return: str - Local Mean Solar Time

		"""
		if utc_date==None:
			utc_date = UTCDateTime().now()

		if isinstance(utc_date, UTCDateTime):
			jd_utc = self.utcDateTime_to_jdutc(utc_date)
			#print("jd_utc: ", jd_utc)
		elif isinstance(utc_date, str):
			try:
				utc_date_in_utc = UTCDateTime(utc_date)
				utc_date = utc_date_in_utc
			except TypeError:
				return None
			else:
				jd_utc = self.utcDateTime_to_jdutc(utc_date_in_utc)

		jd_tt = self.julian_tt(jday_utc=jd_utc)
		jd_ott = self.j2000_offset_tt(jd_tt)

		origin_in_sec = self.__origindate.timestamp
		#origin_in_sec = self.SOL01_START_TIME.timestamp
		any_date_in_sec = utc_date.timestamp

		delta_sec = any_date_in_sec - origin_in_sec
		#print("delta_sec: ", delta_sec)
		#print("martian sol :",delta_sec / (self.SECOND_IN_A_DAY*self.SOL_RATIO))
		martianSol = floor(delta_sec / (self.SECOND_IN_A_DAY*self.SOL_RATIO))
		#martianSol = int(delta_sec / (self.SECONDS_PER_MARS_DAY))
		raw_martian_sol = delta_sec / (self.SECONDS_PER_MARS_DAY)
		#print(raw_martian_sol, martianSol)
		#LMST Calculation
		MLST = self._LMST(longitude=self.__longitude, j2000_ott=jd_ott)
		#print("MLST", MLST)
	   #Conversion to time format
		ihour = floor(MLST)
		minutes = (MLST - ihour)*60.
		iminutes = floor(minutes)
		seconds = (minutes - iminutes)*60.
		iseconds = floor(seconds)
		milliseconds = int(math.modf((seconds-iseconds)*1000000)[1])
		#print(minutes, seconds, seconds-iseconds)
		#correction_factor = 0.0
		#milliseconds -=int(correction_factor*1000)
		if output == "decimal":
			marsDate  = raw_martian_sol
			#marsDate = float(martianSol)+MLST/24.
		else:
			# output updated with v1.3
			if MLST > 23.99:
				marsDate = "{:04}T{:02}:{:02}:{:02}.{:09}".format(martianSol-1,ihour,\
								iminutes, iseconds, milliseconds)
			else: 
				marsDate = "{:04}T{:02}:{:02}:{:02}.{:09}".format(martianSol,ihour,\
								iminutes, iseconds, milliseconds)

		return marsDate


	def get_utc_2_lmst_2tab(self, utc_date = None):
		"""
		Convert UTC date to LMST date into a list 
		----
		INPUT:
			@utc_date: UTCDateTime
		----
		OUTPUT:
			@return: list - Local Mean Solar Time 
					[SOL, Hour, Minutes, Second, milliseconds]]

		"""
		if utc_date==None:
			utc_date = UTCDateTime().now()

		if isinstance(utc_date, UTCDateTime):
			jd_utc = self.utcDateTime_to_jdutc(utc_date)

		elif isinstance(utc_date, str):
			try:
				utc_date_in_utc = UTCDateTime(utc_date)
				utc_date = utc_date_in_utc
			except TypeError:
				return None
			else:
				jd_utc = self.utcDateTime_to_jdutc(utc_date_in_utc)

		jd_tt = self.julian_tt(jday_utc=jd_utc)
		jd_ott = self.j2000_offset_tt(jd_tt)

		origin_in_sec = self.__origindate.timestamp
		any_date_in_sec = utc_date.timestamp

		delta_sec = any_date_in_sec - origin_in_sec
		
		martianSol = int(delta_sec / (self.SECOND_IN_A_DAY*self.SOL_RATIO))

		#LMST Calculation
		MLST = self._LMST(longitude=self.__longitude, j2000_ott=jd_ott)

		#Conversion to time format
		ihour = floor(MLST)
		minutes = (MLST - ihour)*60.
		iminutes = floor(minutes)
		seconds = (minutes - iminutes)*60.
		iseconds = floor(seconds)
		milliseconds = int(math.modf((seconds-iseconds)*1000)[1])
		#correction_factor = 0.0
		#milliseconds -=int(correction_factor*1000)
		marsDate = [martianSol, ihour, iminutes, iseconds, milliseconds]

		return marsDate

	def get_lmst_to_utc(self, lmst_date = None):
		"""
		Function to estimate the UTC time giving a LMST time.
		
		LMST Time must have the following formar : XXXXTMM:MM:ss.mmm
		with : 
			SSSS : number of sols
			HH: Hours
			MM: Minutes
			ss: Seconds
			mmm: miliseconds
		
		----
		INPUT
			@lmst_date: string
		
		----
		OUPUT
			@return: Time with UTCDateTime format

		"""
		from obspy import UTCDateTime

		if lmst_date==None:
			return UTCDateTime.now()
		else:
			date2split = str(lmst_date)


			whereTpos = date2split.find("T")
			#print("whereTpos", whereTpos)
			# mars date format: XXXXTMM:MM:SS.mmm
			if whereTpos > 0:
				# extract the number of SOLS
				nbsol = float(date2split[:whereTpos])

				# extract hour time in a list
				timepart = date2split[whereTpos+1:].split(":")

				# result in martian hours
				#hours_in_dec = float(timepart[0]) + float(timepart[1])/60 + \
				#			float(timepart[2])/(60*60) + \
				#			float(timepart[3])/(1000*60*60)

				if len(timepart) == 2:     #only hh:mm
					hours_in_dec = float(timepart[0]) + float(timepart[1])/60
				elif len(timepart) == 3:   # hh:mm:ss.sssssss 
					hours_in_dec = float(timepart[0]) + float(timepart[1])/60 + \
								float(timepart[2])/(60*60)
				#elif len(timepart) == 3:  # hh:mm:ss:sssssss (previous format with colons as separator of decimal)
				#	hours_in_dec = float(timepart[0]) + float(timepart[1])/60 + \
				#			float(timepart[2])/(60*60) + \
				#			float(timepart[3])/(1000*60*60)
				else:
					hours_in_dec = None


				jd_utc_orig = self.utcDateTime_to_jdutc(self.get_origindate())
				jd_tt_orig = self.julian_tt(jday_utc=jd_utc_orig)

				jd_ott_orig = self.j2000_offset_tt(jd_tt_orig)

				MTC = self.Coordinated_Mars_Time(jd_ott_orig)

				# Add the number of SOL to the MTC of the origin date
				MTC+=nbsol*24

				# Add the number of hours to the MTC of the origin date
				if hours_in_dec is not None: 
					MTC+=hours_in_dec
	
					# Get back to Delta J2000 (Eq 15)
					JD_OTT = (MTC/24 - self.KNORM + self.K)*self.SOL_RATIO + 4.5
	
					# Equation A6 from MARS 24 (https://www.giss.nasa.gov/tools/mars24/help/algorithm.html)
					JD_TT = JD_OTT + self.CONSISTENT_JULIAN_DAY
	
					# Equation A2 from MARS 24
					JD_UT = JD_TT - 69.184/86400
	
					# Equation A1 from MARS 24
					UTC = (JD_UT - self.JULIAN_UNIX_EPOCH)*self.MILLISECONDS_IN_A_DAY/1000.
	
					return UTCDateTime(UTC)
				else:
					return None

			# Case where you just give the a number of SOL
			elif whereTpos < 0 or whereTpos == None:

				# Extract the MTC time of the "origin time" (time where SOL 0 starts)
				#orig = self.get_origindate().timestamp

				jd_utc_orig = self.utcDateTime_to_jdutc(self.get_origindate())
				jd_tt_orig = self.julian_tt(jday_utc=jd_utc_orig)

				jd_ott_orig = self.j2000_offset_tt(jd_tt_orig)

				MTC = self.Coordinated_Mars_Time(jd_ott_orig)
				MTC+=float(date2split)*24

				# Get back to Delta J2000 (Eq 15)
				JD_OTT = (MTC/24 - self.KNORM + self.K)*self.SOL_RATIO + 4.5

				# Equation A6 from MARS 24 (https://www.giss.nasa.gov/tools/mars24/help/algorithm.html)
				JD_TT = JD_OTT + self.CONSISTENT_JULIAN_DAY

				# Equation A2 from MARS 24
				JD_UT = JD_TT - 69.184/86400

				# Equation A1 from MARS 24
				UTC = (JD_UT - self.JULIAN_UNIX_EPOCH)*self.MILLISECONDS_IN_A_DAY/1000.

				#checkSOL = self.get_utc_2_lmst(UTCDateTime(UTC))
				#print("checkSOL", checkSOL)
				#print("date2split", date2split)
				correction_factor = .466
				return UTCDateTime(UTC)+correction_factor
			else:
				return None

	#==========================================================================
	# Additionnal Calculations
	#    added in 19', Nov 26th
	#==========================================================================

	def solar_declination(self,utc_date = None):
		"""
		Determine solar declination (planetographic). (AM1997, eq. D5)
		----
		INPUT:
			@utc_date: 
		
		"""
		if isinstance(utc_date, UTCDateTime):
			jd_utc = self.utcDateTime_to_jdutc(utc_date)

		elif isinstance(utc_date, str):
			try:
				utc_date_in_utc = UTCDateTime(utc_date)
				utc_date = utc_date_in_utc
			except TypeError:
				return None
			else:
				jd_utc = self.utcDateTime_to_jdutc(utc_date_in_utc)

		jd_tt = self.julian_tt(jday_utc=jd_utc)
		jd_ott = self.j2000_offset_tt(jd_tt)
		ls = self.L_s(jd_ott)
		delta_s = (180/math.pi)*math.asin(0.42565*math.sin(math.pi*ls/180)) \
			+ 0.25* math.sin(math.pi*ls/180)   # (-> AM1997, eq. D5)
		return delta_s


	def local_solar_elevation(self, utc_date = None):
		"""
		For any given point on Mars's surface, 
		we want to determine the angle of the sun. 
		
		From section D-5 on Mars24 algo page
		
		added in dec 19, 19th
		"""
		if isinstance(utc_date, UTCDateTime):
			jd_utc = self.utcDateTime_to_jdutc(utc_date)

		elif isinstance(utc_date, str):
			try:
				utc_date_in_utc = UTCDateTime(utc_date)
				utc_date = utc_date_in_utc
			except TypeError:
				return None
			else:
				jd_utc = self.utcDateTime_to_jdutc(utc_date_in_utc)
		jd_tt = self.julian_tt(jday_utc=jd_utc)
		jd_ott = self.j2000_offset_tt(jd_tt)
		
		MTC = self.Coordinated_Mars_Time(j2000_ott = jd_ott)
		MTC= MTC%24
		#print("\t -MTC= ", MTC)
		delta_s = self.solar_declination(utc_date = utc_date)
		#print("\t -deltas= ", delta_s)
	
		lbda    = self.LONGITUDE
		lbda    = lbda%360
		#print("\t -lbda= ", lbda)
		phi     = self.LATITUDE

		EOT = self.equation_of_time(j2000_ott=jd_ott)
		#print("\t -Equation of time:", EOT)
		lbda_s = MTC*(360/24) + EOT + 180
		lbda_s = lbda_s%360
		#print("\t -lbda_s=", lbda_s)
		
		d2r = math.pi/180.
		
		H = lbda -lbda_s
		#print("\t -H=", H)
		Z = (180/math.pi)*math.acos(math.sin(delta_s*d2r)*math.sin(phi*d2r)+\
				math.cos(delta_s*d2r)*math.cos(phi*d2r)*math.cos(H*d2r)) 
		#print("\t -Z=", Z)
		solar_elevation = 90 - Z
		return solar_elevation



	def local_solar_azimuth(self, utc_date = None):
		"""
		For any given point on Mars's surface, 
		we want to determine the angle of the sun. 
		
		From section D-6 on Mars24 algo page
		
		added in dec 19, 19th
		"""
		if isinstance(utc_date, UTCDateTime):
			jd_utc = self.utcDateTime_to_jdutc(utc_date)

		elif isinstance(utc_date, str):
			try:
				utc_date_in_utc = UTCDateTime(utc_date)
				utc_date = utc_date_in_utc
			except TypeError:
				return None
			else:
				jd_utc = self.utcDateTime_to_jdutc(utc_date_in_utc)
		jd_tt = self.julian_tt(jday_utc=jd_utc)
		jd_ott = self.j2000_offset_tt(jd_tt)
		
		MTC = self.Coordinated_Mars_Time(j2000_ott = jd_ott)
		MTC= MTC%24
		#print("\t -MTC= ", MTC)
		delta_s = self.solar_declination(utc_date = utc_date)
		#print("\t -deltas= ", delta_s)
	
		lbda    = self.LONGITUDE
		lbda    = lbda%360
		#print("\t -lbda= ", lbda)
		phi     = self.LATITUDE

		EOT = self.equation_of_time(j2000_ott=jd_ott)
		#print("\t -Equation of time:", EOT)
		lbda_s = MTC*(360/24) + EOT + 180
		lbda_s = lbda_s%360
		#print("\t -lbda_s=", lbda_s)
		
		d2r = math.pi/180
		
		H = lbda -lbda_s
		#print("\t -H=", H)
		A = (180/math.pi)*math.atan(math.sin(H*d2r)/\
					   (math.cos(phi*d2r)*math.tan(delta_s*d2r)-math.sin(phi*d2r)*math.cos(H*d2r))) 
		A = A%360
		#print("\t -A=", A)
		return A



if __name__ == '__main__':
	import sys
	from pathlib import Path

	print("Welcome in MarsConverter module.")
	print("This main is just a test...")
	landerconfigfile = './landerconfig.xml'
	
	my_file = Path(landerconfigfile)

	if my_file.is_file():
		print("Config file found")
		UTCDate = UTCDateTime.now()
		print("Now is ", UTCDate)
		mDate = MarsTimeConverter()
		marsDateNow = mDate.get_utc_2_lmst()
		posT = marsDateNow.find('T')
		
		print("in LMST, now, it is ", marsDateNow)
		print("SOL ",marsDateNow[:posT] ,"from ", \
			str(mDate.get_lmst_to_utc(lmst_date=int(marsDateNow[:posT]))), \
			" UTC to ", str(mDate.get_lmst_to_utc(lmst_date=(int(marsDateNow[:posT])+1))))
		
		print("UTC Date Time: {}".format(UTCDate))
		print("From utc to lmst (formated):",  mDate.get_utc_2_lmst(utc_date=UTCDate))
		print("From utc to lmst (decimal):",  mDate.get_utc_2_lmst(utc_date=UTCDate, output="decimal"))
		print("From utc to ltst          : ", mDate.get_utc_2_ltst(utc_date=UTCDate))
		print("Solar declination: {}".format(mDate.solar_declination(utc_date=UTCDate)))
		print("Solar elevation : {}".format(mDate.local_solar_elevation(utc_date=UTCDate)))
		print("Solar azimuth   : {}".format(mDate.local_solar_azimuth(utc_date=UTCDate)))
		print("--------------------------")
		print("Another example...")
		#Example with a given UTCDateTime
		#UTCDate = "2019-10-15T11:05:34.123456Z"
		#2019-06-30T05:58
		UTCDate = "2019-06-12T06:28:0.0"
		print("UTC Date Time: {}".format(UTCDate))
		print("From utc to lmst (formated):",  mDate.get_utc_2_lmst(utc_date=UTCDate))
		print("From utc to lmst (decimal):",  mDate.get_utc_2_lmst(utc_date=UTCDate, output="decimal"))
		print("From utc to ltst          : ", mDate.get_utc_2_ltst(utc_date=UTCDate))
		print("Solar declination: {}".format(mDate.solar_declination(utc_date=UTCDate)))
		print("Solar elevation : {}".format(mDate.local_solar_elevation(utc_date=UTCDate)))
		print("Solar azimuth   : {}".format(mDate.local_solar_azimuth(utc_date=UTCDate)))
		
		
	else: 
		sys.exit("No config file found")
