""" Holder of the TimeValue class and a function to build one given a JSON representation of it. """

import datetime
from functools import singledispatch
from typing import Union
from typing_extensions import TypeGuard

import tfsl.interfaces as I
import tfsl.languages
import tfsl.utils

class TimeValue:
    """ Representation of a date or time in Wikibase. """
    def __init__(self, time: str,
        before: int=0, after: int=0, precision: int=11, timezone: int=0,
        calendarmodel: str=tfsl.utils.prefix_wd("Q1985727")):
        self.time: str = time
        self.timezone: int = timezone
        self.before: int = before
        self.after: int = after
        self.precision: int = precision
        self.calendarmodel: str = calendarmodel

    def __jsonout__(self) -> I.TimeValueDict:
        base_dict: I.TimeValueDict = {
            "time": self.time,
            "timezone": self.timezone,
            "before": self.before,
            "after": self.after,
            "precision": self.precision,
            "calendarmodel": self.calendarmodel
        }
        return base_dict

@singledispatch
def to_TimeValue(obj_in: object, precision: int=11) -> TimeValue: # pylint: disable=invalid-name
    """ Intended to convert arbitrary objects to TimeValues. """
    raise ValueError(f"Can't convert {type(obj_in)} to TimeValue")

@to_TimeValue.register(datetime.date)
@to_TimeValue.register(datetime.datetime)
def _(obj_in: Union[datetime.datetime, datetime.date], precision: int=11) -> TimeValue:
    if precision > 11:
        raise ValueError("Precisions smaller than day are not supported (T57755)")
    timestr = obj_in.strftime("+%Y-%m-%dT00:00:00Z") + '/' + str(precision)
    return TimeValue(timestr, precision=precision)

def is_TimeValue(value_in: I.ClaimDictValueDictionary) -> TypeGuard[I.TimeValueDict]: # pylint: disable=invalid-name
    """ Checks that the keys expected for a TimeValue exist. """
    return all(key in value_in for key in ["time", "precision"])

def build_TimeValue(value_in: I.TimeValueDict) -> TimeValue: # pylint: disable=invalid-name
    """ Builds a TimeValue given the Wikibase JSON for one. """
    return TimeValue(**value_in)
