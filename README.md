# Mars Time Converter - Useful tools to convert UTC Time to/from Mars Time

## Table of content
1.  Version
2.  Contact
3.  What is is ?
4.  How to install it ?
5.  How to use it ? 
6.  How is it calculated ?


---

## 1. Version 
* **2019-12-19 - v1.6 - Add functions to calculate solar elevation and azimuth at landing site.**
* 2019-12-12 - v1.5 - Add function to convert UTC Date to Local True Solar Time (LTST) (@f031fa57)
* 2019-11-27 - v1.4 - MatLab version added -> utc2lmst function implemented.
* 2019-10-22 - v1.3 - Colons artefact in LMST date fixed.
* 2019-10-21 - v1.2 - Shell scripts added to convert "utc to lmst" (-> utc2lmst) and "lmst to utc (->lmst2utc)
* 2019-10-20 - v1.1 - Shell script added to get current lmst date from terminal windows.
* 2019-10-17 - v1.0 - First release.


## 2. Contact 
Grégory Sainton - IPGP (Institut de Physique du Globe de Paris) - sainton@ipgp.fr
on behalf InSight/SEIS collaboration.

## 3. What is it  ?

Mars Time Converter is a project developped for InSight collaboration to convert UTC Time to/from Mars Time (LMST).
Note that for moment, MarsTimeConverter is only converting to LMST (Local Mars Solar Time).
It's also made of additionnal scripts to ease your life.


### 3.1 MarsTimeConverter.py

Nothing much to say about the file. If you need implementation details see the 
last section "How is it calculated ? "

It's running with **Python 3**
If you need to install Python 3, here is a link : [https://www.anaconda.com/distribution/](https://www.anaconda.com/distribution/)
Then select the package depending on you OS (Linux, Mac, Windows)


Just to make sure you have all the packages, here is the import section: 

```
import os
import math
from math import floor
import time
import numpy as np
```
As explained below, obspy is also necessary
```
from obspy import UTCDateTime
```

### 3.2 The configuration file: landerconfigfile.xml
This file is an xml file with the following structure (example for the InSight Lander): 

```
<configlanding>
        <landingdate>2018-330T19:44:52.444</landingdate>
        <longitude>224.03</longitude>
        <solorigin>2018-330T05:10:50.3356</solorigin>
</configlanding>
```

It contains landing time and longitude. 
For curious guys,"solorigin" is the landing date shifted to make sure that 
we don't have weird behaviours between the SOL number and the time (which are 
calculated independantly).
Trick which has been given to by Robert B. Schmunk from [Mars24 Sunclock](https://www.giss.nasa.gov/tools/mars24/)

### 3.3 Additionnal shell scripts
#### 3.3.1 marsnow
This allows user to get current LMST date from terminal window.
To be able to use it from anywhere, please add the following environement variable 
$MARSCONVERTER to your $PYTHONPATH variable and to you $PATH (to use shell scripts)
$MARSCONVERTER is the path to the directory containing MarsConverter stuffs.

Example : 

```
export MARSCONVERTER=paths/to/marstimeconverter
export PYTHONPATH=$PYTHONPATH:$MARSCONVERTER
export PATH=$PATH:$MARSCONVERTER
```

Don't forget the 

```
source .bash_profile
```

to update $PYTHONPATH (if your setup is in the .bash_profile, of course. Otherwise, 
change to your own shell file).

**->TRICK** : One can add the script to its .bash_profile to execute it each time 
one open a new terminal.

Example : 
```
# Mars Converter
export MARSCONVERTER=path/to/marsconverter
export PYTHONPATH="$MARSCONVERTER:$PYTHONPATH"

bash marsnow
```

#### 3.3.2 utc2lmst
Script to convert UTC Date Time to LMST date.
As marsnow, $MARSCONVERTER must be set first. See above.

Examples:
```
$utc2lmst -d "2019-10-21T12:34:43.453445"
$utc2lmst -d "2019-10-21"
```

### 3.3.3 lmst2utc
Script to convert LMST date to UTC Date
As marsnow and utc2lmst, $MARSCONVERTER must be set first. See above.

Example:
```
$utc2lmst -d "173T12:34:43.453445"
```

*Please note that the decimal separation between second and milliseconds is also 
colons (":"). It's a weird thing which will be fixed soon.* **-> Fixed with v1.3, no more relevant.**

### 3.4 MarsTimeConverterMatlab.m

This program is the same as the python version. 

## 4. How to install it ?

### 4.1. Prerequisites

Since MarsTimeConverter has been developped in the same time as some other functions 
to analyse seismic signals from Mars, it is still dependant from obspy project. 
So, you need to install it before using MarsConverter

To install obspy : [https://github.com/obspy/obspy/wiki/Installation-via-Anaconda)](https://github.com/obspy/obspy/wiki/Installation-via-Anaconda)

### 4.2 MarsTimeConverter 

You can either direclty **copy the files** wherever you want or **you can clone** this 
repository on your computer to keep an active link and get updates if any, in 
the future.


*  To clone : In a terminal, 

```
git clone git@github.com:GregS1t/marstimeconverter.git

```


*  To download : click on the little cloud to download. Then unzip or untar the archive.

## 5. How to use it ?

In the main part of the file and example is given: 

```
print("Welcome in MarsTimeConverter module.")
landerconfigfile = './landerconfig.xml'
my_file = Path(landerconfigfile)

```
One needs to create an instance of the class MarsTimeConverter which will be used all
the time after
```
mDate = MarsTimeConverter(landerconfigfile)

```
If no argument is given to the fonction get_utc_2_lmst(), it will convert current time to lmst
For example: 
```
marsDateNow = mDate.get_utc_2_lmst()
posT = marsDateNow.find('T')

print("Today, it is ", marsDateNow)
print("SOL ",marsDateNow[:posT] ,"from ", \
	str(mDate.get_lmst_to_utc(lmst_date=int(marsDateNow[:posT]))), \
	" UTC to ", str(mDate.get_lmst_to_utc(lmst_date=(int(marsDateNow[:posT])+1))))
```
Example with a given UTCDateTime 
```
UTCDate = "2019-10-15T11:05:34.123456Z"
print("From utc to lmst (formated):",  mDate.get_utc_2_lmst(utc_date=UTCDate))
print("From utc to lmst (decimal):",  mDate.get_utc_2_lmst(utc_date=UTCDate, output="decimal"))
```
In the previous example, you can either get the LMST in a formatted way or in decimal.

## 6. How is it calculated ? 

I encourage you to visit the help pages of Mars24 SunClock which gives all the steps of the algorithm.
Here is the link: [https://www.giss.nasa.gov/tools/mars24/help/algorithm.html](https://www.giss.nasa.gov/tools/mars24/help/algorithm.html)
Original algo. was developped in the following article : [https://pubs.giss.nasa.gov/abs/al05000n.html](https://pubs.giss.nasa.gov/abs/al05000n.html) 
but be careful, numerical data were updated.




