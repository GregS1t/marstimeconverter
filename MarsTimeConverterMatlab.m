%% MarsTimeConvertor
%  @ December 2018, 7th
%   This module is a class "Mars Converter" designed to convert UTC Time to LMST Time and LMST Time to UTC Time
%   LMST Time is depending on the landing time and the longitude of the lander.
% 
%     
%     Matlab function which contains all the function to convert UTC time 
%     to Martian Time.
%
%     All the calculation are based of the Mars 24 algorithm itself based on
%     Alison, McEwen, Planetary ans Space Science 48 (2000) 215-235
%     https://www.giss.nasa.gov/tools/mars24/help/algorithm.html
%
%     
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
% THIS MATLAB FUNCTION IS A TRANSLATION OF THE MarsConverter.ipynb written
% by G. Sainton for ASPIC program
% @ A. LUCAS, 18 Dec. 2018. version 1.0 - Original from MarsConverter.ipynb
% @ G. Sainton, 27 Nov 2018. version 1.1 - Update and bugs fixed
% @ G. Sainton, 01 Mar 2021. version 1.2 - fix utc2lmst error calculation < 1/2 second

%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
global JULIAN_UNIX_EPOCH MILLISECONDS_IN_A_DAY SHIFT_IN_DAY_PER_DEGREE
global CONSISTENT_JULIAN_DAY  TAI_UTC TIME_COEFFICIENT MMULTIPLIER
global K  KNORM SOL_RATIO j2000_epoch SECOND_IN_DAY
 
%% GLOBAL VARIABLES

JULIAN_UNIX_EPOCH = 2440587.5 ;         % JULIAN UNIX EPOCH (01/01/1970-00:00 UTC)
MILLISECONDS_IN_A_DAY = 86400000.0;     % MILLISECONDS IN A DAY
SHIFT_IN_DAY_PER_DEGREE = 1. / 360.0;   % SHIFT IN DAY PER DEGREE
%# Julian day of reference (january 2010, 6th 00:00 UTC) At that time, the martian meridian is also à midnight.
CONSISTENT_JULIAN_DAY = 2451545.0;
TAI_UTC = 0.0003725;                    % Delta between IAT and UTC
TIME_COEFFICIENT = 60.0;                % Time division
MMULTIPLIER = 1000.0;                   % Millisecond multiplier
K = 0.0009626;                          % Allison's coefficient
KNORM = 44796.0;                        % Allison's normalisation factor
SOL_RATIO = 1.027491252;                % Ratio Betwwen Martian SOL and terrestrial day
j2000_epoch = 2451545.0;
SECOND_IN_DAY = 86400.0;                %#SECOND IN A DAY
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
%% LANDER CONFIG DATA 

% Insight Informations
%     - Landing date   26 November 2018, 19:52:59 UTC
%     - Landing site   Elysium Planitia: 4.5°N 135.0°E

global landingdate origindate longitude
landingdate = datetime(2018, 11, 26, 19, 44, 52.444, 'TimeZone','Etc/GMT');
origindate  = datetime(2018, 11, 26,  5, 10, 50.336037, 'TimeZone','Etc/GMT'); 
longitude   = 224.03;
 
%% TEST PART
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
%utc_date = datetime('now','TimeZone','Etc/GMT','Format','d-MMM-y HH:mm:ss Z')
% utc_date = datetime(2018, 11, 26, 19, 44, 34.123456, 'TimeZone','Etc/GMT')
% 
% 
%  
% disp('UTC time:')
% disp(utc_date)
%  
% disp('Mars time:')
% marsDate = utc2lmst(utc_date, "dec")
% disp(marsDate)
% 
% marsDate = utc2lmst(utc_date, "tab")
% disp(marsDate)
% marsDate = utc2lmst(utc_date, "date")
% disp(marsDate) 
%~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
%% FUNCTIONS

function out=mills(time)
global MMULTIPLIER
%     """Returns the current time in milliseconds since Jan 1 1970"""
out= time*MMULTIPLIER;
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function out=julian(date)
global JULIAN_UNIX_EPOCH  MILLISECONDS_IN_A_DAY
millis = posixtime(utc_date) * 1000.0;
out =  JULIAN_UNIX_EPOCH + (millis/MILLISECONDS_IN_A_DAY);
disp("julian", out)
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function out=utc_to_tt_offset(jday)
%    """
% Returns the offset in seconds from a julian date in Terrestrial Time (TT)
%to a Julian day in Coordinated Universal Time (UTC)
%"""
out =  utc_to_tt_offset_math(jday);
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function out=utc_to_tt_offset_math(jday)
%         """
%         Returns the offset in seconds from a julian date in Terrestrial Time (TT)
%         to a Julian day in Coordinated Universal Time (UTC)
%         """
 
jday_np = jday;
jday_min = 2441317.5;
 
jday_vals = [     -2441317.5 0.    182.    366. ...
    731.   1096.   1461.   1827. ...
    2192.,  2557.   2922.   3469. ...
    3834.   4199.   4930.   5844....
    6575.   6940.   7487.  7852. ...
    8217.   8766.   9313.   9862. ...
    12419.  13515. 14792. 15887. 16437.];
 
offset_min = 32.184;
 
offset_vals = [-32.184 10. 11.0,12.0, 13.0 ...
    14.0 15.0 16.0 17.0 18.0 ...
    19.0 20.0 21.0 22.0 23.0 ...
    24.0 25.0 26.0 27.0 28.0 ...
    29.0 30.0 31.0 32.0 33.0 ...
    34.0 35.0 36.0 37.0];
 
if jday_np <= jday_min+jday_vals(1)
    out= offset_min+offset_vals(1);
elseif jday_np >= jday_min+jday_vals(end)
    out= offset_min+offset_vals(end);
else
    for i=1:numel(offset_vals)
        if (jday_min+jday_vals(i) <= jday_np)  && (jday_min+jday_vals(i+1) > jday_np)
            out= offset_min+offset_vals(i);
        end
    end
end
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function jdtt=julian_tt(jday_utc)
%         """
%         Returns the TT Julian Day given a UTC Julian day
%         """
jdtt = jday_utc + utc_to_tt_offset(jday_utc)/86400.;
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function out=j2000_offset_tt(jday_tt)
%         """
%         Returns the julian day offset since the J2000 epoch
%         Equation 15
%         """
global j2000_epoch
out = jday_tt - j2000_epoch;
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function Mmod=Mars_Mean_Anomaly(j2000_ott)
%  """Calculates the Mars Mean Anomaly given a j2000 julian day offset"""
 
M = 19.3871 + 0.52402073 * j2000_ott;
Mmod = mod(M, 360);
%disp(Mmod)
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function out=Alpha_FMS(j2000_ott)
%  """Returns the Fictional Mean Sun angle"""
out=   mod(270.3871 + 0.524038496 * j2000_ott,360);
 
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function pbs=alpha_perturbs(j2000_ott)
%   """Returns the perturbations to apply to the FMS Angle from orbital perturbations"""
 
A = [0.0071, 0.0057, 0.0039, 0.0037, 0.0021, 0.0020, 0.0018];
tau = [2.2353, 2.7543, 1.1177, 15.7866, 2.1354, 2.4694, 32.8493];
phi = [49.409, 168.173, 191.837, 21.736, 15.704, 95.528, 49.095];
 
pbs=sum(A.*cos(((0.985626 * j2000_ott./tau) + phi).*pi/180.));
 
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function val=equation_of_center(j2000_ott)
%         """
%         The true anomaly (v) - the Mean anomaly (M)
%         """
 
M = Mars_Mean_Anomaly(j2000_ott)*pi/180;
pbs = alpha_perturbs(j2000_ott);
 
val = (10.691 + 3.0e-7 * j2000_ott)*sin(M) ...
    + 0.6230 * sin(2*M) ...
    + 0.0500 * sin(3*M) ...
    + 0.0050 * sin(4*M) ...
    + 0.0005 * sin(5*M)  ...
    + pbs;
 
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function ls = L_s(j2000_ott)
%     """Returns the Areocentric solar longitude (aka Ls)"""
 
alpha = Alpha_FMS(j2000_ott);
v_m   = equation_of_center(j2000_ott);
 
ls = (alpha + v_m);
ls =  mod(ls, 360);
 
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function EOT=equation_of_time(j2000_ott)
%   """Equation of Time, to convert between Local Mean Solar Time
%    and Local True Solar Time, and make pretty analemma plots"""
 
ls = L_s(j2000_ott)*pi/180.;
 
EOT = 2.861*sin(2*ls) ...
    - 0.071 * sin(4*ls) ...
    + 0.002 * sin(6*ls) - equation_of_center(j2000_ott);
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function j2000_ott=j2000_from_Mars_Solar_Date(msd)
    %     Returns j2000 based on MSD
    j2000_ott = ((msd + 0.00096 - 44796.0) * 1.027491252) + 4.5;
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function out=j2000_ott_from_Mars_Solar_Date(msd)
    %    Returns j2000 offset based on MSD"""
    global j2000_epoch
    j2000 = j2000_from_Mars_Solar_Date(msd);
    j2000_ott = julian_tt(j2000+j2000_epoch);
    out= j2000_ott-j2000_epoch;
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function MSD=Mars_Solar_Date(j2000_ott)
    global SOL_RATIO  KNORM K
    %        """Return the Mars Solar date"""
    const = 4.5;
    MSD = (((j2000_ott - const)/SOL_RATIO) + KNORM - K);
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function  MTC=Coordinated_Mars_Time(j2000_ott)
    %         """
    %         The Mean Solar Time at the Prime Meridian
    %         Equation 22
    %         """
    global KNORM K SOL_RATIO
    MTC = 24 * (((j2000_ott - 4.5)/SOL_RATIO) + KNORM - K);
    %MTC = mod(MTC, 24);
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function LMST=Local_Mean_Solar_Time(longitude, j2000_ott)
    %         """
    %         The Local Mean Solar Time given a planetographic longitude
    %         """
    MTC = Coordinated_Mars_Time(j2000_ott);
    disp(['MTC =', num2str(MTC)])
    MTCmod = mod(MTC,24);
    LMST = mod((MTCmod - longitude * (24./360.)), 24);
    %disp(['MTCMod =', num2str(MTCmod),'    LMST = ',num2str(LMST)])
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
 
function ltst=Local_True_Solar_Time(longitude, j2000_ott)
    %         
    %         Local true solar time is the Mean solar time + equation of time perturbation
    %         Equation 23 / Equation 24
    %
    eot = equation_of_time(j2000_ott);
    lmst = Local_Mean_Solar_Time(longitude, j2000_ott);
    ltst = mod((lmst + eot*(1./15.)),24);
 
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
 
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
function jd_utc=utcDateTime_to_jdutc(date)
    global JULIAN_UNIX_EPOCH MILLISECONDS_IN_A_DAY

    millis = posixtime(date) * 1000.0;
    jd_utc = JULIAN_UNIX_EPOCH + ((millis) / MILLISECONDS_IN_A_DAY);
 
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~

function marsDate=utc2lmst(utc_date, fmt)
    % ﻿
    % 	Convert UTC date to LMST date into a list 
    % 	----
    % 	INPUT:
    % 		@utc_date: 
    % 	----
    % 	OUTPUT:
    % 		@return: list - Local Mean Solar Time 
    % 				[SOL, Hour, Minutes, Second, milliseconds]]
    % 	
    global JULIAN_UNIX_EPOCH MILLISECONDS_IN_A_DAY SECOND_IN_DAY 
    global SOL_RATIO
    global origindate longitude
    ts = (datenum(utc_date) - datenum('01-Jan-1970 00:00:00'))*86400;
    millis = ts * 1000.0;
    jd_utc = (JULIAN_UNIX_EPOCH + (millis / MILLISECONDS_IN_A_DAY));
    jd_tt = julian_tt(jd_utc);
    jd_ott = j2000_offset_tt(jd_tt);

    delta_sec = seconds(utc_date - origindate);
    martianSol = delta_sec / (SECOND_IN_DAY*SOL_RATIO);
    nbsol       = floor(martianSol);
    
    hour_dec = 24*(martianSol - fix(martianSol));
    ihour       = floor(hour_dec);
    
    min_dec  = 60*(hour_dec - ihour);
    imin        =  floor(min_dec); 
    
    second    = 60*(min_dec-imin);
    isec         = floor(second);
    
    millisec    = (second-isec)*100000;
    
    if fmt == "dec"
        marsDate = martianSol;    
    elseif fmt == "tab"
        marsDate = [fix(martianSol), fix(ihour), fix(imin), fix(isec), fix(millisec)];
    elseif fmt == "date"
        marsDate = strcat(num2str(fix(martianSol)),"T",num2str(ihour),":" ,num2str(imin),":", num2str(isec),".",num2str(millisec));
    else 
        disp("Unknown format")
    end
end
%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~%~~~~~~~~~~~~~~~~~~~~
