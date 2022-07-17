import datetime
from functools import singledispatch
from typing_extensions import TypeGuard

import tfsl.interfaces as I
import tfsl.languages
import tfsl.utils

class TimeValue:
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
def toTimeValue(obj_in: object) -> TimeValue:
    raise ValueError("Can't convert " + str(type(obj_in)) + " to TimeValue")

@toTimeValue.register
def _(obj_in: datetime.datetime) -> TimeValue:
    raise NotImplementedError

@toTimeValue.register
def _(obj_in: datetime.date) -> TimeValue:
    raise NotImplementedError

def is_timevalue(value_in: I.ClaimDictValueDictionary) -> TypeGuard[I.TimeValueDict]:
    return all(key in value_in for key in ["time", "precision"])

def build_timevalue(value_in: I.TimeValueDict) -> TimeValue:
    return TimeValue(**value_in)
