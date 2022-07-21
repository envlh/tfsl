""" Holder of the QuantityValue class and a function to build one given a JSON representation of it. """

from typing_extensions import TypeGuard

import tfsl.interfaces as I
import tfsl.languages
import tfsl.utils

class QuantityValue:
    """ Representation of a quantity in Wikibase. """
    def __init__(self, amount: float=0, lowerBound: float=1, upperBound: float=-1, unit: str=tfsl.utils.prefix_wd("Q199")):
        self.amount: float = amount
        self.lower: float
        self.upper: float
        if lowerBound >= upperBound:
            self.lower = amount
            self.upper = amount
        else:
            self.lower = lowerBound
            self.upper = upperBound
        if not I.is_Qid(unit):
            unit = tfsl.utils.strip_prefix_wd(unit)
        self.unit: str = unit

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, QuantityValue):
            return NotImplemented
        amts_equal = self.amount == rhs.amount
        lowers_equal = self.lower == rhs.lower
        uppers_equal = self.upper == rhs.upper
        units_equal = self.unit == rhs.unit
        return amts_equal and lowers_equal and uppers_equal and units_equal

    def __hash__(self) -> int:
        return hash((self.amount, self.lower, self.upper, self.unit))

    def __str__(self) -> str:
        if(self.lower == self.amount and self.upper == self.amount):
            value_string = f'{self.amount}'
        else:
            value_string = f'{self.amount}[{self.lower},{self.upper}]'
        unit_string = ""
        if self.unit != "Q199":
            unit_string = f' {self.unit}'
        return value_string + unit_string

    def __jsonout__(self) -> I.QuantityValueDict:
        base_dict: I.QuantityValueDict = {
            "amount": self.amount,
            "unit": tfsl.utils.prefix_wd(self.unit)
        }
        if(self.lower != self.amount or self.upper != self.amount):
            base_dict["lowerBound"] = self.lower
            base_dict["upperBound"] = self.upper
        return base_dict

def is_quantityvalue(value_in: I.ClaimDictValueDictionary) -> TypeGuard[I.QuantityValueDict]:
    """ Checks that the keys expected for a QuantityValue exist. """
    return all(key in value_in for key in ["amount", "unit"])

def build_quantityvalue(value_in: I.QuantityValueDict) -> QuantityValue:
    """ Builds a QuantityValue given the Wikibase JSON for one. """
    return QuantityValue(**value_in)
