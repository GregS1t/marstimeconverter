"""
test_converter.py

Test and demo script for MarsTimeConverter. Parses the configuration XML,
instantiates time converters for several Mars missions, and continuously
updates and displays Local Mean Solar Time (LMST) using a refresh loop.

This script is primarily intended for manual testing and visualization.
"""


import os
import sys
import logging
from datetime import datetime, timezone
from lxml import etree
from marstimeconverter.converter import MarsTimeConverter, DEFAULT_CONFIG_FILE
from marstimeconverter.plotting import refresh_lmst_display

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """
    Entry point for the test script.

    - Checks the presence of the configuration XML file.
    - Loads default mission and UTC time.
    - Instantiates MarsTimeConverter for multiple missions.
    - Launches LMST refresh display loop.

    Exits the script with an error if the configuration is invalid or missing.
    """
    if os.path.isfile(DEFAULT_CONFIG_FILE):
        try:
            tree = etree.parse(DEFAULT_CONFIG_FILE)
            root = tree.getroot()
        except Exception as e:
            logging.error(f"Invalid XML configuration file: {e}")
            sys.exit(1)

        current_utc = datetime.now(timezone.utc)
        logging.info(f"Current UTC time: {current_utc}")

        # Define available missions.
        mission_dict = {0: "Mars", 1: "Perseverance", 2: "Curiosity",
                        3: "Opportunity", 4: "Spirit", 5: "InSight",
                        6: "Zhurong"}
        mission = mission_dict[2]
        logging.info(f"Default mission for test: {mission}")

        mDate = MarsTimeConverter(mission=mission)

        # Create multiple mission instances for comparison.
        MTC_missions = [MarsTimeConverter(mission=mission_dict[0]),
                        MarsTimeConverter(mission=mission_dict[2]),
                        MarsTimeConverter(mission=mission_dict[3]),
                        MarsTimeConverter(mission=mission_dict[4])]
        logging.info("Starting UTC to LMST test (refresh every 1 second)...")
        refresh_lmst_display(MTC_missions, frequency=1.0)
    else:
        sys.exit("Configuration file not found.")

if __name__ == '__main__':
    main()
