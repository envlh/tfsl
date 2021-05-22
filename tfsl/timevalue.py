from functools import singledispatchmethod
import json
import datetime

import tfsl.languages
import tfsl.utils

def matches_time(arg):
    # TODO: fill in and use
    pass

class TimeValue:
    def __init__(self, time, before=0, after=0, precision=11, timezone=0, calendarmodel="http://www.wikidata.org/entity/Q1985727"):
        self.time = time
        self.timezone = timezone
        self.before = before
        self.after = after
        self.precision = precision
        self.calendarmodel = calendarmodel
    
    def __jsonout__(self):
        base_dict = {
                   "time": self.time,
                   "timezone": self.timezone,
                   "before": self.before,
                   "after": self.after,
                   "precision": self.precision,
                   "calendarmodel": self.calendarmodel
               }
        return base_dict

@singledispatch
def toTimeValue(obj_in):
    raise ValueError("Can't convert " + str(type(obj_in)) + " to TimeValue")

@toTimeValue.register
def _(obj_in: datetime.datetime):
    pass

@toTimeValue.register
def _(obj_in: datetime.date):
    pass

def build_timevalue(value_in):
    return TimeValue(**value_in)
