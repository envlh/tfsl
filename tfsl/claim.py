""" Holder of the Claim class and a function to build one given a JSON representation of it. """

from typing import Dict, Optional, Union, overload

import tfsl.interfaces as I
import tfsl.coordinatevalue
import tfsl.itemvalue
import tfsl.monolingualtext
import tfsl.quantityvalue
import tfsl.timevalue
import tfsl.utils

type_string_to_type: Dict[str, type] = {
    'string': str,
    'globecoordinate': tfsl.coordinatevalue.CoordinateValue,
    'monolingualtext': tfsl.monolingualtext.MonolingualText,
    'quantity': tfsl.quantityvalue.QuantityValue,
    'time': tfsl.timevalue.TimeValue,
    'wikibase-entityid': tfsl.itemvalue.ItemValue
}

class Claim:
    """ Representation of a claim, or a property-predicate pair.
        These may be added to statements directly, as qualifiers, or as parts of references.
    """
    def __init__(self, property_in: I.Pid, value: I.ClaimValue):
        self.property: I.Pid = property_in
        self.value: I.ClaimValue
        self.datatype: str = tfsl.utils.values_datatype(self.property)
        if tfsl.utils.is_novalue(value) or tfsl.utils.is_somevalue(value):
            self.value = value
        else:
            value_type = type(value)
            property_type = type_string_to_type[tfsl.utils.external_to_internal_type_mapping[self.datatype]]
            if property_type == value_type:
                self.value = value
            else:
                raise TypeError(f"Providing {value_type} as {property_in} value where {property_type} expected")

        self.snaktype: Optional[str] = None
        self.hash: Optional[str] = None

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, Claim):
            return NotImplemented
        return self.property == rhs.property and self.value == rhs.value

    def __hash__(self) -> int:
        return hash((self.property, self.value))

    def __str__(self) -> str:
        return f'{self.property}: {self.value}'

    def __jsonout__(self) -> I.ClaimDict:
        snaktype: str = "value"
        value_out: Optional[I.ClaimDictValue] = None
        datavalue_out: Optional[I.ClaimDictDatavalue] = None

        if isinstance(self.value, bool):
            if self.value is False:
                snaktype = "novalue"
            elif self.value is True:
                snaktype = "somevalue"
        elif isinstance(self.value, str):
            value_out = self.value
        else:
            value_out = self.value.__jsonout__()
        if value_out is not None:
            datavalue_out = {
                "value": value_out,
                "type": tfsl.utils.values_type(self.property)
            }

        claimdict_out: I.ClaimDict = {
            "snaktype": snaktype,
            "property": self.property,
            "datatype": tfsl.utils.values_datatype(self.property),
        }
        if datavalue_out is not None:
            claimdict_out["datavalue"] = datavalue_out
        return claimdict_out

    def get_ItemValue(self,
                      novalue: Optional[tfsl.itemvalue.ItemValue]=None,
                      somevalue: Optional[tfsl.itemvalue.ItemValue]=None) -> tfsl.itemvalue.ItemValue:
        if isinstance(self.value, tfsl.itemvalue.ItemValue):
            return self.value
        if self.value is True and somevalue is not None:
            return somevalue
        if self.value is False and novalue is not None:
            return novalue
        raise TypeError(f"{self.property} statement did not yield an ItemValue")

    def get_MonolingualText(self,
                      novalue: Optional[tfsl.monolingualtext.MonolingualText]=None,
                      somevalue: Optional[tfsl.monolingualtext.MonolingualText]=None) -> tfsl.monolingualtext.MonolingualText:
        if isinstance(self.value, tfsl.monolingualtext.MonolingualText):
            return self.value
        if self.value is True and somevalue is not None:
            return somevalue
        if self.value is False and novalue is not None:
            return novalue
        raise TypeError(f"{self.property} statement did not yield a MonolingualText")

    def get_str(self,
                      novalue: Optional[str]=None,
                      somevalue: Optional[str]=None) -> str:
        if isinstance(self.value, str):
            return self.value
        if self.value is True and somevalue is not None:
            return somevalue
        if self.value is False and novalue is not None:
            return novalue
        raise TypeError(f"{self.property} statement did not yield a string")

@overload
def build_value(actual_value: I.QuantityValueDict) -> tfsl.quantityvalue.QuantityValue: ...
@overload
def build_value(actual_value: I.MonolingualTextDict) -> tfsl.monolingualtext.MonolingualText: ...
@overload
def build_value(actual_value: I.CoordinateValueDict) -> tfsl.coordinatevalue.CoordinateValue: ...
@overload
def build_value(actual_value: I.TimeValueDict) -> tfsl.timevalue.TimeValue: ...
@overload
def build_value(actual_value: I.ItemValueDict) -> tfsl.itemvalue.ItemValue: ...
@overload
def build_value(actual_value: str) -> str: ...

def build_value(actual_value: Union[str, I.ClaimDictValueDictionary]) -> I.ClaimValue:
    """ Builds a ClaimValue given the Wikibase JSON for one. """
    if isinstance(actual_value, str):
        return actual_value
    elif tfsl.itemvalue.is_itemvalue(actual_value):
        return tfsl.itemvalue.build_itemvalue(actual_value)
    elif tfsl.monolingualtext.is_mtvalue(actual_value):
        return tfsl.monolingualtext.build_mtvalue(actual_value)
    elif tfsl.coordinatevalue.is_coordinatevalue(actual_value):
        return tfsl.coordinatevalue.build_coordinatevalue(actual_value)
    elif tfsl.quantityvalue.is_quantityvalue(actual_value):
        return tfsl.quantityvalue.build_quantityvalue(actual_value)
    elif tfsl.timevalue.is_timevalue(actual_value):
        return tfsl.timevalue.build_timevalue(actual_value)
    raise ValueError(f"Attempting to build value of unsupported type")

def build_claim(claim_in: I.ClaimDict) -> Claim:
    """ Builds a Claim given the Wikibase JSON for one. """
    claim_prop: I.Pid
    claim_value: I.ClaimValue

    claim_prop = claim_in["property"]
    if claim_in["snaktype"] == 'novalue':
        claim_value = False
    elif claim_in["snaktype"] == 'somevalue':
        claim_value = True
    else:
        claim_datavalue = claim_in["datavalue"]
        claim_value = build_value(claim_datavalue["value"])

    claim_out = Claim(claim_prop, claim_value)
    claim_out.snaktype = claim_in["snaktype"]
    claim_out.hash = claim_in["hash"]
    claim_out.datatype = claim_in["datatype"]
    return claim_out
