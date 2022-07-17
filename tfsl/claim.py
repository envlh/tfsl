from typing import Optional

import tfsl.interfaces as I
import tfsl.utils

class Claim:
    """ Representation of a claim, or a property-predicate pair.
        These may be added to statements directly, as qualifiers, or as parts of references.

        CHECKS THAT THE VALUE MATCHES THE PROPERTY'S TYPE ARE NOT PERFORMED!
        YOU ARE RESPONSIBLE FOR ENSURING THAT THESE MATCH!
    """
    def __init__(self, property_in: I.Pid, value: I.ClaimValue):
        self.property: I.Pid = property_in
        self.value: I.ClaimValue = value

        self.snaktype: Optional[str] = None
        self.hash: Optional[str] = None
        self.datatype: str = tfsl.utils.values_datatype(self.property)

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

def build_value(value_in: I.ClaimDictDatavalue) -> I.ClaimValue:
    value_type = value_in["type"]
    actual_value = value_in["value"]
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
    else:
        raise ValueError(f"Type {value_type} is not supported yet!")

def build_claim(claim_in: I.ClaimDict) -> Claim:
    claim_prop: I.Pid
    claim_value: I.ClaimValue

    claim_prop = claim_in["property"]
    if claim_in["snaktype"] == 'novalue':
        claim_value = False
    elif claim_in["snaktype"] == 'somevalue':
        claim_value = True
    else:
        claim_value = build_value(claim_in["datavalue"])

    claim_out = Claim(claim_prop, claim_value)
    claim_out.snaktype = claim_in["snaktype"]
    claim_out.hash = claim_in["hash"]
    claim_out.datatype = claim_in["datatype"]
    return claim_out
