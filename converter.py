import os
import math
import time
import numpy as np
from datetime import datetime, timezone, timedelta
from lxml import etree
import logging
from marstimeconverter.helpers import deprecated

# Configure logging for this module.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Improved configuration handling
CONFIG_PATH = os.getenv('MARSCONVERTER')
if not CONFIG_PATH:
    raise EnvironmentError("Environment variable 'MARSCONVERTER' not set. Please set it appropriately.")

DEFAULT_CONFIG_FILE = os.path.join(CONFIG_PATH, "marstimeconverter",
                                   "CONFIG", "mission_config_file.xml")

class MarsTimeConverter:
    """
    Class for converting UTC time to Martian time (LMST) and performing additional calculations
    based on the Mars24 algorithm.
    """
    # Constants
    JULIAN_UNIX_EPOCH = 2440587.5
    MILLISECONDS_IN_A_DAY = 86400000.0
    SECONDS_IN_A_DAY = 86400.0
    SECONDS_IN_A_SOL = 88775.0
    CONSISTENT_JULIAN_DAY = 2451545.0
    TAI_UTC = 0.0003725
    TIME_COEFFICIENT = 60.0
    K = 0.0009626
    KNORM = 44796.0
    SOL_RATIO = 1.0274912517
    MARS_MILLIS_IN_A_YEAR = 59355000000
    MARS_SOLS_IN_YEAR = 668.5991

    # InSight mission reference times
    SOL01_START_TIME = datetime.fromisoformat("2018-11-27T05:50:25.580014+00:00")
    SOL02_START_TIME = datetime.fromisoformat("2018-11-28T06:30:00.823990+00:00")
    SECONDS_PER_MARS_DAY = (SOL02_START_TIME - SOL01_START_TIME).total_seconds() - 0.000005

    def __init__(self, mission_config_file: str = None, mission: str = "InSight"):
        """
        Initialize the MarsTimeConverter using the XML configuration file
        for the specified mission.

        Args:
            mission_config_file (str, optional): Path to the XML configuration
                file. If not provided, uses the default.
            mission (str, optional): Name of the Mars mission (e.g., "InSight",
                "Curiosity"). Defaults to "InSight".

        Raises:
            ValueError: If the configuration file is missing, malformed, or
                does not contain data for the specified mission.
        """
        
        self.configfile = mission_config_file or DEFAULT_CONFIG_FILE

        try:
            tree = etree.parse(self.configfile)
        except Exception as e:
            raise ValueError(f"Error parsing configuration file '{self.configfile}': {e}")

        root = tree.getroot()
        lander_element = root.find(f"./lander[@name='{mission}']")
        if lander_element is None:
            raise ValueError(f"No configuration found for mission '{mission}'")

        landing_date_str = lander_element.findtext("landingdate")
        landing_longitude = float(lander_element.findtext("longitude"))
        landing_latitude = float(lander_element.findtext("latitude"))
        sol_origin_str = lander_element.findtext("solorigin")
        solorigin_elem = lander_element.find("solorigin")
        if solorigin_elem is None or solorigin_elem.get("ref") is None:
            raise ValueError("No valid <solorigin> element with 'ref' attribute found in configuration.")
        solorigin_ref = int(solorigin_elem.get("ref"))
        landing_site = lander_element.findtext("landing_site")

        self.__landingdate = self._parse_datetime(landing_date_str)
        self.__origindate = self._parse_datetime(sol_origin_str)
        self.__sol_ref = solorigin_ref
        self.__longitude = landing_longitude
        self.__landing_site = landing_site
        self.LONGITUDE = float(landing_longitude)
        self.LATITUDE = landing_latitude
        self.mission = mission

    def _parse_datetime(self, dt_input):
        """
        Convert a string or naive datetime into a timezone-aware UTC datetime
        object.

        Supports ISO 8601 format or year-day-of-year format.

        Args:
            dt_input (str or datetime): Date input to convert.

        Returns:
            datetime: A timezone-aware datetime object in UTC.

        Raises:
            TypeError: If the input is neither a string nor a datetime object.
        """
        if isinstance(dt_input, datetime):
            return dt_input if dt_input.tzinfo else dt_input.replace(tzinfo=timezone.utc)
        elif isinstance(dt_input, str):
            try:
                dt_obj = datetime.fromisoformat(dt_input)
            except ValueError:
                try:
                    dt_obj = datetime.strptime(dt_input, "%Y-%jT%H:%M:%S.%f")
                except ValueError:
                    dt_obj = datetime.strptime(dt_input, "%Y-%jT%H:%M:%S")
            return dt_obj if dt_obj.tzinfo else dt_obj.replace(tzinfo=timezone.utc)
        else:
            raise TypeError("Unsupported date format. Expected string or datetime.")

    def get_landing_date(self) -> datetime:
        """
        Return the landing date of the mission in UTC.

        Returns:
            datetime: The landing date as a timezone-aware UTC datetime.
        """
        return self.__landingdate

    def get_landing_site(self) -> str:
        """
        Return the name of the landing site.

        Returns:
            str: Name of the Mars landing site.
        """
        return self.__landing_site

    def get_longitude(self) -> float:
        """
        Return the longitude of the mission's landing site.

        Returns:
            float: Longitude in degrees.
        """
        return self.__longitude

    def get_origindate(self) -> datetime:
        """
        Return the sol origin date in UTC.

        Returns:
            datetime: Sol origin date as a timezone-aware UTC datetime.
        """
        return self.__origindate

    def get_sol_origin_ref(self) -> int:
        """
        Return the sol origin reference number.

        Returns:
            int: The sol reference value (typically 0 or 1).
        """
        return self.__sol_ref

    def get_j2000_epoch(self) -> float:
        """
        Return the J2000 epoch as a Julian day number.

        Returns:
            float: J2000 epoch value in Julian days.
        """
        return self.CONSISTENT_JULIAN_DAY

    def get_millis(self) -> float:
        """
        Return the current time in milliseconds since the Unix epoch.

        Returns:
            float: Time in milliseconds.
        """
        return time.time() * 1000.0

    def utc2julian(self, date: datetime = None) -> float:
        """
        Calculate the Julian day number for a given UTC datetime.

        This uses equation A-2 from the Mars24 algorithm.

        Args:
            date (datetime, optional): UTC datetime. If None, uses current UTC.

        Returns:
            float: Julian day number.
        """
        date = self._parse_datetime(date) if date else datetime.now(timezone.utc)
        millis = date.timestamp() * 1000.0
        return self.JULIAN_UNIX_EPOCH + (millis / self.MILLISECONDS_IN_A_DAY)

    def utc2tt_offset(self, jday: float = None) -> float:
        """
        Return the offset in seconds from UTC to Terrestrial Time (TT).

        Uses the mathematical approximation from equation A-3.

        Args:
            jday (float, optional): Julian day. If None, current UTC is used.

        Returns:
            float: TT offset in seconds.
        """
        return self.utc2tt_offset_math(jday)

    def utc2tt_offset_math(self, jday: float = None) -> float:
        """
        Compute the offset in seconds from UTC to TT using predefined tables.

        Uses equation A-4 from the Mars24 algorithm.

        Args:
            jday (float, optional): Julian day. If None, current UTC is used.

        Returns:
            float: TT offset in seconds.
        """
        jday_np = self.utc2julian() if jday is None else jday
        jday_min = 2441317.5
        jday_vals = [-2441317.5, 0, 182, 366, 731, 1096, 1461, 1827,
                     2192, 2557, 2922, 3469, 3834, 4199, 4930, 5844,
                     6575, 6940, 7487, 7852, 8217, 8766, 9313, 9862,
                     12419, 13515, 14792, 15887, 16437]
        offset_min = 32.184
        offset_vals = [-32.184, 10.0, 11.0, 12.0, 13.0,
                       14.0, 15.0, 16.0, 17.0, 18.0,
                       19.0, 20.0, 21.0, 22.0, 23.0,
                       24.0, 25.0, 26.0, 27.0, 28.0,
                       29.0, 30.0, 31.0, 32.0, 33.0,
                       34.0, 35.0, 36.0, 37.0]
        if jday_np <= jday_min + jday_vals[0]:
            return offset_min + offset_vals[0]
        elif jday_np >= jday_min + jday_vals[-1]:
            return offset_min + offset_vals[-1]
        else:
            for i in range(len(offset_vals) - 1):
                if (jday_min + jday_vals[i] <= jday_np) and (jday_min + jday_vals[i+1] > jday_np):
                    return offset_min + offset_vals[i]
            return offset_min + offset_vals[-1]

    def utc2julian_tt(self, jday_utc: float = None) -> float:
        """
        Convert a UTC Julian day to a TT Julian day.

        Uses equation A-5 from the Mars24 algorithm.

        Args:
            jday_utc (float, optional): UTC Julian day. Defaults to now.

        Returns:
            float: TT Julian day.
        """
        if jday_utc is None:
            jday_utc = self.utc2julian()
        return jday_utc + self.utc2tt_offset(jday_utc) / self.SECONDS_IN_A_DAY

    def delta_t_j2000(self, jday_tt: float = None) -> float:
        """
        Compute the time offset from the J2000 epoch in TT.

        Uses equation A-6 from the Mars24 algorithm.

        Args:
            jday_tt (float, optional): TT Julian day. Defaults to current TT.

        Returns:
            float: Offset from J2000 in Julian days.
        """
        if jday_tt is None:
            jday_tt = self.utc2julian_tt()
        return jday_tt - self.get_j2000_epoch()

    def mars_mean_anomaly(self, j2000_offset: float = None) -> float:
        """
        Calculate the Mars Mean Anomaly (M) in degrees.

        Uses equation B-1 from AM2000, eq. 16.

        Args:
            j2000_offset (float, optional): Offset from J2000. Defaults to now.

        Returns:
            float: Mars Mean Anomaly in degrees.
        """
        if j2000_offset is None:
            j2000_offset = self.delta_t_j2000()
        M = 19.3871 + 0.52402073 * j2000_offset
        return M % 360.0

    def alpha_fms(self, j2000_offset: float = None) -> float:
        """
        Calculate the Fictional Mean Sun (FMS) angle.

        Uses equation B-2 from AM2000, eq. 17.

        Args:
            j2000_offset (float, optional): Offset from J2000. Defaults to now.

        Returns:
            float: FMS angle in degrees.
        """
        if j2000_offset is None:
            j2000_offset = self.delta_t_j2000()
        alpha = 270.3871 + 0.524038496 * j2000_offset
        return alpha % 360.0

    def pbs(self, j2000_offset: float = None) -> float:
        """
        Calculate the periodic perturbations to the mean Sun angle (PBS).

        Uses equation B-3 from AM2000, eq. 18.

        Args:
            j2000_offset (float, optional): Offset from J2000. Defaults to now.

        Returns:
            float: Perturbation angle in degrees.
        """
        if j2000_offset is None:
            j2000_offset = self.delta_t_j2000()
        array_A = [0.0071, 0.0057, 0.0039, 0.0037, 0.0021, 0.0020, 0.0018]
        array_tau = [2.2353, 2.7543, 1.1177, 15.7866, 2.1354, 2.4694, 32.8493]
        array_phi = [49.409, 168.173, 191.837, 21.736, 15.704, 95.528, 49.095]
        pbs_val = 0.0
        for A, tau, phi in zip(array_A, array_tau, array_phi):
            pbs_val += A * np.cos(((0.985626 * j2000_offset / tau) + phi) * math.pi / 180.0)
        return pbs_val

    def equation_of_center(self, j2000_offset: float = None) -> float:
        """
        Calculate the Equation of Center (EOC), the angular difference
        between the true and mean anomaly.

        Uses equation B-4 from the Mars24 algorithm.

        Args:
            j2000_offset (float, optional): Offset from J2000. Defaults to now.

        Returns:
            float: Equation of Center in degrees.
        """
        if j2000_offset is None:
            j2000_offset = self.delta_t_j2000()
        M_rad = self.mars_mean_anomaly(j2000_offset) * math.pi / 180.0
        eoc = ((10.691 + 3.0e-7 * j2000_offset) * math.sin(M_rad) +
               0.6230 * math.sin(2 * M_rad) +
               0.0500 * math.sin(3 * M_rad) +
               0.0050 * math.sin(4 * M_rad) +
               0.0005 * math.sin(5 * M_rad) +
               self.pbs(j2000_offset))
        return eoc

    def l_s(self, j2000_offset: float = None) -> float:
        """
        Calculate the areocentric solar longitude (Ls).

        This angle defines Mars’s position in its orbit relative to the Sun.

        Uses equation B-5 from the Mars24 algorithm.

        Args:
            j2000_offset (float, optional): Offset from J2000. Defaults to now.

        Returns:
            float: Solar longitude (Ls) in degrees.
        """
        if j2000_offset is None:
            j2000_offset = self.delta_t_j2000()
        ls_angle = (self.alpha_fms(j2000_offset) + self.equation_of_center(j2000_offset)) % 360.0
        return ls_angle

    #
    # C- Determine Mars Time
    #

    def equation_of_time(self, j2000_offset: float = None) -> float:
        """
        Calculate the Equation of Time (EOT), the difference between
        solar time and mean solar time.

        Uses equation C-1 from the Mars24 algorithm.

        Args:
            j2000_offset (float, optional): Offset from J2000. Defaults to now.

        Returns:
            float: Equation of Time in degrees.
        """
        if j2000_offset is None:
            j2000_offset = self.delta_t_j2000()
        ls_rad = self.l_s(j2000_offset) * math.pi / 180.0
        eot = (2.861 * math.sin(2 * ls_rad) -
               0.071 * math.sin(4 * ls_rad) +
               0.002 * math.sin(6 * ls_rad) -
               self.equation_of_center(j2000_offset))
        return eot

    def mars_sol_date(self, j2000_offset: float = None) -> float:
        """
        Calculate the Mars Sol Date (MSD), the Martian equivalent of
        Julian Day.

        Uses equation C-2 from the Mars24 algorithm.

        Args:
            j2000_offset (float, optional): Offset from J2000. Defaults to now.

        Returns:
            float: Mars Sol Date.
        """
        if j2000_offset is None:
            jday_tt = self.utc2julian_tt()
            j2000_offset = self.delta_t_j2000(jday_tt)
        msd = (((j2000_offset - 4.5) / self.SOL_RATIO) + self.KNORM - 0.00096)
        return msd

    def mean_solar_time(self, j2000_offset: float = None) -> float:
        """
        Calculate the Mean Solar Time (MST) at Mars’s prime meridian.

        This is the average solar time without accounting for the Equation
        of Time.

        Args:
            j2000_offset (float, optional): Offset from J2000. Defaults to now.

        Returns:
            float: Mean Solar Time in decimal hours.
        """
        mst = (24 * (((self.utc2julian_tt() - 2451549.5) / self.SOL_RATIO) + self.KNORM - self.K)) % 24
        return mst

    def coordinated_mars_time(self, j2000_offset: float = None) -> float:
        """
        Calculate the Coordinated Mars Time (MTC), similar to UTC on Earth.

        Args:
            j2000_offset (float, optional): Offset from J2000. Defaults to now.

        Returns:
            float: Coordinated Mars Time in decimal hours.
        """
        return self.mean_solar_time(j2000_offset) % 24.0

    #
    # D. Additional Calculations
    #

    def solar_declination(self, utc_date=None) -> float:
        """
        Calculate the solar declination angle on Mars for a given UTC date.

        Uses equation D-1 from the Mars24 algorithm.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
                Defaults to current UTC time.

        Returns:
            float: Solar declination angle in degrees.
        """
        utc_date = self._parse_datetime(utc_date) if utc_date else datetime.now(timezone.utc)
        jd_utc = self.datetime2jdutc(utc_date)
        jd_tt = self.utc2julian_tt(jday_utc=jd_utc)
        j2000_offset = self.delta_t_j2000(jd_tt)
        ls_deg = self.l_s(j2000_offset)
        decl = (180 / math.pi) * math.asin(0.42565 * math.sin(math.radians(ls_deg))) + 0.25 * math.sin(math.radians(ls_deg))
        return decl

    def local_solar_elevation(self, utc_date=None) -> float:
        """
        Calculate the local solar elevation angle on Mars.

        Uses equation D-5 from the Mars24 algorithm.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
                Defaults to current UTC time.

        Returns:
            float: Solar elevation angle in degrees.
        """
        utc_date = self._parse_datetime(utc_date) if utc_date else datetime.now(timezone.utc)
        jd_utc = self.datetime2jdutc(utc_date)
        jd_tt = self.utc2julian_tt(jday_utc=jd_utc)
        j2000_offset = self.delta_t_j2000(jd_tt)
        mtc = self.coordinated_mars_time(j2000_offset) % 24
        decl = self.solar_declination(utc_date)
        lbda = self.LONGITUDE % 360
        phi = self.LATITUDE
        eot = self.equation_of_time(j2000_offset)
        lbda_s = (mtc * (360 / 24) + eot + 180) % 360
        d2r = math.pi / 180.0
        H = lbda - lbda_s
        zenith_angle = math.degrees(math.acos(math.sin(decl * d2r) * math.sin(phi * d2r) +
                                              math.cos(decl * d2r) * math.cos(phi * d2r) * math.cos(H * d2r)))
        return 90 - zenith_angle

    def local_solar_azimuth(self, utc_date=None) -> float:
        """
        Calculate the local solar azimuth angle on Mars.

        Uses equation D-5 from the Mars24 algorithm.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
                Defaults to current UTC time.

        Returns:
            float: Solar azimuth angle in degrees.
        """
        utc_date = self._parse_datetime(utc_date) if utc_date else datetime.now(timezone.utc)
        jd_utc = self.datetime2jdutc(utc_date)
        jd_tt = self.utc2julian_tt(jday_utc=jd_utc)
        j2000_offset = self.delta_t_j2000(jd_tt)
        mtc = self.coordinated_mars_time(j2000_offset) % 24
        decl = self.solar_declination(utc_date)
        lbda = self.LONGITUDE % 360
        phi = self.LATITUDE
        eot = self.equation_of_time(j2000_offset)
        lbda_s = (mtc * (360 / 24) + eot + 180) % 360
        d2r = math.pi / 180.0
        H = lbda - lbda_s
        azimuth = math.degrees(math.atan(math.sin(H * d2r) /
                                         (math.cos(phi * d2r) * math.tan(decl * d2r) - math.sin(phi * d2r) * math.cos(H * d2r))))
        return azimuth % 360

    #
    # Function often used in programms
    # 

    def get_sol(self, utc_date=None, fmt="decimal"):
        """
        Return the sol number since the mission's sol origin.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
                Defaults to current UTC time.
            fmt (str, optional): "int" returns the integer sol,
                "decimal" returns the sol as a float. Defaults to "decimal".

        Returns:
            int or float: Sol number, either integer or decimal.
        """
        dt = utc_date if isinstance(utc_date, datetime) else self._parse_datetime(utc_date)
        origin_sec = self.__origindate.timestamp()
        dt_sec = dt.timestamp()
        delta_sec = dt_sec - origin_sec
        raw_sol = delta_sec / self.SECONDS_PER_MARS_DAY + self.__sol_ref
        return int(math.modf(raw_sol)[1]) if fmt == "int" else float(raw_sol)

    def utc2ls(self, utc_date=None) -> float:
        """
        Convert a UTC date to areocentric solar longitude (Ls).

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
                Defaults to current UTC time.

        Returns:
            float: Ls angle in degrees.
        """
        utc_date = self._parse_datetime(utc_date) if utc_date else datetime.now(timezone.utc)
        jd_utc = self.datetime2jdutc(utc_date)
        jd_tt = self.utc2julian_tt(jday_utc=jd_utc)
        j2000_offset = self.delta_t_j2000(jd_tt)
        return self.l_s(j2000_offset)

    def utc2ltst(self, utc_date=None, output: str = "date"):
        """
        Convert a UTC date to Local True Solar Time (LTST).

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
                Defaults to current UTC time.
            output (str, optional): If "decimal", returns LTST in float hours.
                If "date", returns formatted sol time. Defaults to "date".

        Returns:
            str or float: LTST as a formatted string or decimal hours.
        """
        utc_date = self._parse_datetime(utc_date) if utc_date else datetime.now(timezone.utc)
        jd_utc = self.datetime2jdutc(utc_date)
        jd_tt = self.utc2julian_tt(jday_utc=jd_utc)
        j2000_offset = self.delta_t_j2000(jd_tt)
        eot = self.equation_of_time(j2000_offset)
        lmst_val = self.utc2lmst(utc_date=utc_date, output="decimal")
        ltst_decimal = lmst_val + eot / 15.0
        sol_num = self.get_sol(utc_date=utc_date, fmt="int")
        if ltst_decimal < 0:
            sol_num -= 1
        elif ltst_decimal >= 24:
            sol_num += 1
        ltst_decimal %= 24
        if output == "decimal":
            return ltst_decimal
        else:
            return f"{sol_num:04}T{self._h2hms(ltst_decimal)}"

    def utc2lmst(self, utc_date=None, output: str = "date", split: bool = False):
        """
        Convert a UTC date to Local Mean Solar Time (LMST).

        Args:
            utc_date (datetime, str, or list-like, optional): UTC datetime or
                array-like of dates. Defaults to current UTC time.
            output (str, optional): "decimal" returns float sol;
                "date" returns formatted string. Defaults to "date".
            split (bool, optional): If True, returns [sol, hour, minute,
                second, microsecond]. Defaults to False.

        Returns:
            str, float, or list: LMST as formatted string, float, or list.
        """

        def _convert_single(utc):
            dt = utc if isinstance(utc, datetime) else self._parse_datetime(utc)
            jd_utc = self.datetime2jdutc(dt)
            origin_sec = self.__origindate.timestamp()
            dt_sec = dt.timestamp()
            delta_sec = dt_sec - origin_sec
            raw_sol = delta_sec / self.SECONDS_PER_MARS_DAY + self.__sol_ref
            sol_int = int(math.modf(raw_sol)[1])
            hour_decimal = 24 * math.modf(raw_sol)[0]
            ihour = math.floor(hour_decimal)
            min_decimal = 60 * (hour_decimal - ihour)
            iminute = math.floor(min_decimal)
            seconds_total = (min_decimal - iminute) * 60.0
            iseconds = int(math.modf(seconds_total)[1])
            microseconds = int(math.modf(seconds_total - iseconds)[0] * 1000000)
            if output == "decimal":
                return raw_sol
            elif split:
                return [sol_int, ihour, iminute, iseconds, microseconds]
            else:
                return f"{sol_int:04}T{ihour:02}:{iminute:02}:{iseconds:02}.{microseconds:06}"
        if utc_date is None:
            utc_date = datetime.now(timezone.utc)
        if isinstance(utc_date, (list, tuple, np.ndarray)):
            vectorized_convert = np.vectorize(_convert_single)
            return vectorized_convert(np.array(utc_date))
        else:
            return _convert_single(utc_date)

    def utc2eot(self, utc_date=None) -> float:
        """
        Convert a UTC date to the Equation of Time (EOT).

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
                Defaults to current UTC time.

        Returns:
            float: Equation of Time in degrees.
        """
        utc_date = self._parse_datetime(utc_date) if utc_date else datetime.now(timezone.utc)
        jd_utc = self.datetime2jdutc(utc_date)
        jd_tt = self.utc2julian_tt(jday_utc=jd_utc)
        j2000_offset = self.delta_t_j2000(jd_tt)
        return self.equation_of_time(j2000_offset)

    def datetime2jdutc(self, date: datetime = None) -> float:
        """
        Convert a datetime object to a UTC Julian day number.

        Args:
            date (datetime, optional): UTC datetime. Defaults to current UTC time.

        Returns:
            float: UTC Julian day.
        """
        date = self._parse_datetime(date) if date else datetime.now(timezone.utc)
        millis = date.timestamp() * 1000.0
        return self.JULIAN_UNIX_EPOCH + (millis / self.MILLISECONDS_IN_A_DAY)

    def jdutc2datetime(self, jd_utc: float = None) -> datetime:
        """
        Convert a UTC Julian day number to a datetime object.

        Args:
            jd_utc (float): UTC Julian day.

        Returns:
            datetime: Timezone-aware UTC datetime.
        """
        millis = (jd_utc - self.JULIAN_UNIX_EPOCH) * self.MILLISECONDS_IN_A_DAY
        return datetime.fromtimestamp(millis / 1000.0, tz=timezone.utc)

    def lmst2utc(self, lmst_date=None) -> datetime:
        """
        Convert Local Mean Solar Time (LMST) to UTC datetime.

        Args:
            lmst_date (str or float): LMST formatted string (e.g., "0012T14:25:00")
                or decimal sol time.

        Returns:
            datetime: Corresponding UTC datetime.

        Raises:
            ValueError: If the LMST format is invalid or cannot be parsed.
        """
        if lmst_date is None:
            raise ValueError("lmst_date must be provided")
        s = str(lmst_date).strip()
        try:
            if 'T' in s:
                sol_str, time_str = s.split('T')
                sol_int = int(sol_str)
                try:
                    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
                except ValueError:
                    time_obj = datetime.strptime(time_str, "%H:%M:%S")
                seconds_in_day = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1e6
                frac_day = seconds_in_day / self.SECONDS_IN_A_DAY
                raw_sol = sol_int + frac_day
            else:
                raw_sol = float(s)
            delta_seconds = (raw_sol - self.__sol_ref) * self.SECONDS_PER_MARS_DAY
            return self.get_origindate() + timedelta(seconds=delta_seconds)
        except Exception as e:
            raise ValueError("Invalid LMST format") from e

    def _h2hms(self, hour: float) -> str:
        """
        Convert a decimal hour to a formatted string (HH:MM:SS.microsec).

        Args:
            hour (float): Decimal hour value.

        Returns:
            str: Time formatted as HH:MM:SS.microsec.
        """
        ihour = int(hour)
        min_dec = 60 * (hour - ihour)
        iminutes = int(min_dec)
        seconds = (min_dec - iminutes) * 60.0
        iseconds = int(math.modf(seconds)[1])
        microseconds = int(math.modf(seconds - iseconds)[0] * 1000000)
        return f"{ihour:02}:{iminutes:02}:{iseconds:02}.{microseconds:06}"

    def get_lmst_results(self, utc_date=None) -> dict:
        """
        Compute a dictionary of conversion results for a given UTC date.

        Returns a structured set of Mars time-related values including LMST,
        LTST, Ls, MTC, MSD, and anomalies.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
                Defaults to current UTC time.

        Returns:
            dict: Dictionary of calculated Mars time values.
        """
        dt = (utc_date if isinstance(utc_date, datetime)
              else self._parse_datetime(utc_date) if utc_date
              else datetime.now(timezone.utc))
        jd_utc = self.datetime2jdutc(dt)
        jd_tt = self.utc2julian_tt(jday_utc=jd_utc)
        j2000_offset = self.delta_t_j2000(jd_tt)
        eoc = self.equation_of_center(j2000_offset)
        msd = self.mars_sol_date(j2000_offset)
        mtc = self.coordinated_mars_time(j2000_offset)
        M = self.mars_mean_anomaly(j2000_offset)
        alpha = self.alpha_fms(j2000_offset)
        pbs_val = self.pbs(j2000_offset)
        ltst = self.utc2ltst(utc_date=utc_date)
        raw_sol = self.get_sol(utc_date=dt)
        sol_int = math.floor(raw_sol)
        eot = self.equation_of_time(j2000_offset)
        ls_val = self.l_s(j2000_offset)
        lmst = self.utc2lmst(utc_date=utc_date)
        lmst_utc = self.lmst2utc(lmst_date=lmst)

        return {
            "Earth time (UTC)": dt,
            "Mission Name": self.mission,
            "Latitude": self.LATITUDE,
            "Longitude": self.LONGITUDE,
            "LMST Origin": self.get_origindate(),
            "Landing Site": self.get_landing_site(),
            "UTC Julian Date": jd_utc,
            "TT Julian Date": jd_tt,
            "Delta_t J2000": j2000_offset,
            "Equation of Center": f"{eoc:0.5f}",
            "Mars Sol Date": f"{msd:0.5f}",
            "Coordinated Mars Time (MTC)": self._h2hms(mtc),
            "Mars Mean Anomaly (M)": f"{M:0.5f}",
            "Alpha FMS": f"{alpha:0.5f}",
            "PBS": f"{pbs_val:0.5f}",
            "Ls": f"{ls_val:0.5f}",
            "Equation of Time (EOT)": f"{eot:0.5f}",
            "Raw Martian SOL": f"{raw_sol:0.5f}",
            "Integer SOL": sol_int,
            "LTST": ltst,
            "LMST": lmst,
            "UTC from LMST": lmst_utc
        }

    def utc2lmst_test(self, utc_date=None):
        """
        Print a formatted summary of LMST conversion results to the logger.

        Used for quick testing and debugging.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
                Defaults to current UTC time.
        """
        results = self.get_lmst_results(utc_date=utc_date)
        header = "=" * 80
        logging.info("\n" + header)
        logging.info(f"LMST Conversion Test Results for mission: {self.mission}".center(80))
        logging.info(header)
        for key, value in results.items():
            logging.info(f"{key:35}: {value}")
        logging.info(header + "\n")

    # Deprecated methods for backward compatibility
    @deprecated("utc2lmst")
    def get_utc2lmst(self, utc_date=None, output: str = "date"):
        """
        [Deprecated] Use `utc2lmst()` instead.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
            output (str, optional): "date" or "decimal".

        Returns:
            str or float: Local Mean Solar Time.
        """
        return self.utc2lmst(utc_date=utc_date, output=output)

    @deprecated("lmst2utc")
    def get_lmst2utc(self, lmst_date=None):
        """
        [Deprecated] Use `lmst2utc()` instead.

        Args:
            lmst_date (str or float): LMST input.

        Returns:
            datetime: Corresponding UTC datetime.
        """
        return self.lmst2utc(lmst_date=lmst_date)

    @deprecated("utc2ltst")
    def get_utc2ltst(self, utc_date=None, output: str = "date"):
        """
        [Deprecated] Use `utc2ltst()` instead.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.
            output (str, optional): "date" or "decimal".

        Returns:
            str or float: Local True Solar Time.
        """
        return self.utc2ltst(utc_date=utc_date, output=output)

    @deprecated("utc2ls")
    def get_utc2ls(self, utc_date=None, output: str = "date"):
        """
        [Deprecated] Use `utc2ls()` instead.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.

        Returns:
            float: Areocentric solar longitude (Ls).
        """
        return self.utc2ls(utc_date=utc_date)

    @deprecated("utc2lmst")
    def utc2lmst_2tab(self, utc_date=None):
        """
        [Deprecated] Use `utc2lmst(..., split=True)` instead.

        Args:
            utc_date (datetime or str, optional): UTC datetime or ISO string.

        Returns:
            list: [sol, hour, minute, second, microsecond]
        """
        return self.utc2lmst(utc_date=utc_date, split=True)
