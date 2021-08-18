from functools import singledispatchmethod
import json

import tfsl.languages
import tfsl.utils


class QuantityValue:
    def __init__(self, amount=0, lowerBound=1, upperBound=-1, unit=tfsl.utils.prefix_wd("Q199")):
        self.amount = amount
        if lowerBound >= upperBound:
            self.lower = amount
            self.upper = amount
        else:
            self.lower = lowerBound
            self.upper = upperBound
        if not tfsl.utils.matches_item(unit):
            unit = tfsl.utils.strip_prefix_wd(unit)
        self.unit = unit

    def __eq__(self, rhs):
        amts_equal = self.amount == rhs.amount
        lowers_equal = self.lower == rhs.lower
        uppers_equal = self.upper == rhs.upper
        units_equal = self.unit == rhs.unit
        return amts_equal and lowers_equal and uppers_equal and units_equal

    def __hash__(self):
        return hash((self.amount, self.lower, self.upper, self.unit))

    def __str__(self):
        if(self.lower == self.amount and self.upper == self.amount):
            value_string = f'{self.amount}'
        else:
            value_string = f'{self.amount}[{self.lower},{self.upper}]'
        unit_string = ""
        if self.unit != "Q199":
            unit_string = f' {self.unit}'
        return value_string + unit_string

    def __jsonout__(self):
        base_dict = {
                   "amount": self.amount,
                   "unit": tfsl.utils.prefix_wd(self.unit)
               }
        if(self.lower != self.amount or self.upper != self.amount):
            base_dict["lowerBound"] = self.lower
            base_dict["upperBound"] = self.upper
        return base_dict


def build_quantityvalue(value_in):
    return QuantityValue(**value_in)
