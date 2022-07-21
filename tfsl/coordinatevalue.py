""" Holder of the CoordinateValue class and a function to build one given a JSON representation of it. """

from typing import Optional
from typing_extensions import TypeGuard

import tfsl.interfaces as I
import tfsl.languages
import tfsl.utils

class CoordinateValue:
    """ Representation of a coordinate in Wikibase. """
    def __init__(self, latitude: float, longitude: float, precision: float,
                 globe: str=tfsl.utils.prefix_wd("Q2"), altitude: Optional[float]=None):
        self.lat: float = latitude
        self.lon: float = longitude
        self.prec: float = precision
        self.alt: Optional[float] = altitude
        self.globe: str = globe

    def __jsonout__(self) -> I.CoordinateValueDict:
        base_dict: I.CoordinateValueDict = {
            "latitude": self.lat,
            "longitude": self.lon,
            "altitude": self.alt,
            "precision": self.prec,
            "globe": self.globe
        }
        return base_dict

def is_coordinatevalue(value_in: I.ClaimDictValueDictionary) -> TypeGuard[I.CoordinateValueDict]:
    """ Checks that the keys expected for a CoordinateValue exist. """
    return all(key in value_in for key in ["latitude", "longitude", "altitude", "precision", "globe"])

def build_coordinatevalue(value_in: I.CoordinateValueDict) -> CoordinateValue:
    """ Builds a CoordinateValue given the Wikibase JSON for one. """
    return CoordinateValue(**value_in)
