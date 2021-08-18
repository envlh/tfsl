from functools import singledispatchmethod
import json

import tfsl.languages
import tfsl.utils

class CoordinateValue:
    def __init__(self, latitude, longitude, precision,
                 globe=tfsl.utils.prefix_wd("Q2"), altitude=None):
        self.lat = latitude
        self.lon = longitude
        self.prec = precision
        self.alt = altitude
        self.globe = globe

    def __jsonout__(self):
        base_dict = {
                   "latitude": self.lat,
                   "longitude": self.lon,
                   "altitude": self.alt,
                   "precision": self.prec,
                   "globe": self.globe
               }
        return base_dict


def build_coordinatevalue(value_in):
    return CoordinateValue(**value_in)
