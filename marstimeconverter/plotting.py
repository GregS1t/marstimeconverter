"""
plotting.py

This module provides visualization functions for the MarsTimeConverter tool.
It includes plots for Local Mean Solar Time (LMST), solar longitude (Ls),
solar declination, and comparisons between multiple Mars missions.
"""


import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np

def plot_lmst_vs_utc(mtc_instance, start_utc, num_days, num_points=1000):
    """
    Plot Local Mean Solar Time (LMST) in decimal format as a function of UTC.

    Args:
        mtc_instance (MarsTimeConverter): An instance of the converter.
        start_utc (str or datetime): Start UTC time.
        num_days (int): Number of days to simulate.
        num_points (int, optional): Number of sample points. Defaults to 1000.
    """
    dt_start = mtc_instance._parse_datetime(start_utc)
    total_seconds = num_days * 86400
    time_points = [dt_start + timedelta(seconds=s) for s in np.linspace(0, total_seconds, num_points)]
    lmst_values = [mtc_instance.utc_to_lmst(utc_date=dt, output="decimal") for dt in time_points]

    plt.figure(figsize=(10, 6))
    plt.plot(time_points, lmst_values, label="LMST (decimal)")
    plt.xlabel("UTC Date")
    plt.ylabel("LMST (decimal)")
    plt.title("LMST vs. UTC")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_ls_vs_utc(mtc_instance, start_utc, end_utc, num_points=1000):
    """
    Plot the areocentric solar longitude (Ls) as a function of UTC.

    Args:
        mtc_instance (MarsTimeConverter): An instance of the converter.
        start_utc (str or datetime): Start UTC time.
        end_utc (str or datetime): End UTC time.
        num_points (int, optional): Number of sample points. Defaults to 1000.
    """
    dt_start = mtc_instance._parse_datetime(start_utc)
    dt_end = mtc_instance._parse_datetime(end_utc)
    total_seconds = (dt_end - dt_start).total_seconds()
    time_points = [dt_start + timedelta(seconds=s) for s in np.linspace(0, total_seconds, num_points)]
    ls_values = [mtc_instance.utc_to_ls(utc_date=dt) for dt in time_points]

    plt.figure(figsize=(10, 6))
    plt.plot(time_points, ls_values, label="Ls (degrees)")
    plt.xlabel("UTC Date")
    plt.ylabel("Ls (degrees)")
    plt.title("Areocentric Solar Longitude (Ls) vs. UTC")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_declination_vs_eot(mtc_instance, start_utc, end_utc, num_points=1000):
    """
    Plot solar declination as a function of the Equation of Time (EOT).

    Args:
        mtc_instance (MarsTimeConverter): An instance of the converter.
        start_utc (str or datetime): Start UTC time.
        end_utc (str or datetime): End UTC time.
        num_points (int, optional): Number of sample points. Defaults to 1000.
    """
    dt_start = mtc_instance._parse_datetime(start_utc)
    dt_end = mtc_instance._parse_datetime(end_utc)
    total_seconds = (dt_end - dt_start).total_seconds()
    time_points = [dt_start + timedelta(seconds=s) for s in np.linspace(0, total_seconds, num_points)]
    declinations = [mtc_instance.solar_declination(utc_date=dt) for dt in time_points]
    eot_values = [mtc_instance.get_utc_to_eot(utc_date=dt) for dt in time_points]

    plt.figure(figsize=(10, 6))
    plt.plot(eot_values, declinations, label="Solar Declination vs. EOT")
    plt.xlabel("Equation of Time (degrees)")
    plt.ylabel("Solar Declination (degrees)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def compare_missions_lmst(MTC_missions, utc_date=None):
    """
    Compare LMST conversion results for a list of Mars missions.

    Args:
        MTC_missions (list): List of MarsTimeConverter instances.
        utc_date (datetime or str, optional): UTC time. Defaults to now.
    """
    results = [m.get_lmst_results(utc_date=utc_date) for m in MTC_missions]
    keys = list(results[0].keys())
    key_col_width = 28
    mission_col_width = 33
    header = "=" * (key_col_width + len(results) * (mission_col_width + 3))
    print("\n" + header)
    title = "Comparison of Different Missions"
    print(title.center(len(header)))
    print(header)
    mission_names = [str(r.get("Mission Name", f"Mission {i+1}")) for i, r in enumerate(results)]
    header_line = "".ljust(key_col_width) + " | " + " | ".join(name.ljust(mission_col_width) for name in mission_names)
    print(header_line)
    print("-" * len(header_line))
    for key in keys:
        line = key.ljust(key_col_width) + " | " + " | ".join(str(r.get(key, "")).ljust(mission_col_width) for r in results)
        print(line)
    print(header + "\n")

def refresh_lmst_display(MTC_missions, frequency: float):
    """
    Continuously refresh the LMST display for multiple missions.

    Args:
        MTC_missions (list): List of MarsTimeConverter instances.
        frequency (float): Refresh interval in seconds.
    """
    import os, time
    try:
        while True:
            os.system('clear')
            compare_missions_lmst(MTC_missions, utc_date=None)
            time.sleep(frequency)
    except KeyboardInterrupt:
        print("\nRefresh stopped by user.")
