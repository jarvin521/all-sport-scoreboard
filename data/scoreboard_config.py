from utils import get_file
import json
import os
import debug

DEFAULT_SCROLLING_SPEED = 2
DEFAULT_ROTATE_RATE = 2.0
MINIMUM_ROTATE_RATE = 2.0
DEFAULT_ROTATE_RATES = {"live": DEFAULT_ROTATE_RATE, "final": DEFAULT_ROTATE_RATE, "pregame": DEFAULT_ROTATE_RATE}

class ScoreboardConfig:
    def __init__(self, filename_base, args):
        json = self.__get_config(filename_base)

        # Rotation
        self.rotation_enabled = json["rotation"]["enabled"]
        self.rotation_rates = json["rotation"]["rates"]
        self.scrolling_speed = json["scrolling_speed"]

        # Debug
        self.debug = json["debug"]

        # Check if these are lists or strings
        self.check_rotate_rates()

    def check_rotate_rates(self):
        if isinstance(self.rotation_rates, dict) == False:
            try:
                rate = float(self.rotation_rates)
                self.rotation_rates = {"live": rate, "final": rate, "pregame": rate}
            except:
                debug.warning("rotation_rates should be a Dict or Float. Using default value. {}".format(DEFAULT_ROTATE_RATES))
                self.rotation_rates = DEFAULT_ROTATE_RATES

        for key, value in list(self.rotation_rates.items()):
            try:
                # Try and cast whatever the user passed into a float
                rate = float(value)
                self.rotation_rates[key] = rate
            except:
                # Use the default rotate rate if it fails
                debug.warning("Unable to convert rotate_rates[\"{}\"] to a Float. Using default value. ({})".format(key, DEFAULT_ROTATE_RATE))
                self.rotation_rates[key] = DEFAULT_ROTATE_RATE

            if self.rotation_rates[key] < MINIMUM_ROTATE_RATE:
                debug.warning("rotate_rates[\"{}\"] is too low. Please set it greater than {}. Using default value. ({})".format(key, MINIMUM_ROTATE_RATE, DEFAULT_ROTATE_RATE))
                self.rotation_rates[key] = DEFAULT_ROTATE_RATE

        # Setup some nice attributes to make sure they all exist
        self.rotation_rates_live = self.rotation_rates.get("live", DEFAULT_ROTATE_RATES["live"])
        self.rotation_rates_final = self.rotation_rates.get("final", DEFAULT_ROTATE_RATES["final"])
        self.rotation_rates_pregame = self.rotation_rates.get("pregame", DEFAULT_ROTATE_RATES["pregame"])

    def read_json(self, filename):
        # Find and return a json file

        j = {}
        path = get_file(filename)
        if os.path.isfile(path):
            j = json.load(open(path))
        return j

    def __get_config(self, base_filename):
        # Look and return config.json file

        filename = "{}.json".format(base_filename)
        reference_config = self.read_json(filename)

        return reference_config
