from functools import singledispatchmethod
import json

import tfsl.languages
import tfsl.utils

# TODO: handle non-Wikidata entity prefixes
entity_prefix = 'http://www.wikidata.org/entity/'

class QuantityValue:
    def __init__(self, amount=0, lowerBound=1, upperBound=-1, unit=entity_prefix+"Q199"):
        self.amount = amount
        if(lower >= upper):
            self.lower = amount
            self.upper = amount
        else:
            self.lower = lower
            self.upper = upper
        if not tfsl.utils.matches_item(unit):
            unit = unit[len(entity_prefix):]
        self.unit = unit

    def __eq__(self, rhs):
        return self.amount == rhs.amount and
               self.lower == rhs.lower and
               self.upper == rhs.upper and
               self.unit == rhs.unit

    def __hash__(self):
        return hash((self.amount, self.lower, self.upper, self.unit))
    
    def __str__(self):
        if(self.lower == self.amount and self.upper == self.amount):
            value_string = f'{self.amount}'
        else:
            value_string = f'{self.amount}[{self.lower},{self.upper}]'
        unit_string = ""
        if(self.unit != "Q199"):
            unit_string = f' {self.unit}'
        return value_string + unit_string

    def __jsonout__(self):
        base_dict = {
                   "amount": self.amount,
                   "unit": entity_prefix + self.unit
               }
        if(self.lower != self.amount or self.upper != self.amount):
            base_dict["lowerBound"] = self.lower
            base_dict["upperBound"] = self.upper
        return base_dict

def build_quantityvalue(value_in):
    return QuantityValue(**value_in)
