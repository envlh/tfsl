from functools import singledispatchmethod

import tfsl.utils


class Claim:
    """ Representation of a claim, or a property-predicate pair.
        These may be added to statements directly, as qualifiers, or as parts of references.

        CHECKS THAT THE VALUE MATCHES THE PROPERTY'S TYPE ARE NOT PERFORMED!
        YOU ARE RESPONSIBLE FOR ENSURING THAT THESE MATCH!
    """
    def __init__(self, property_in, value):
        self.property = property_in
        self.value = value

    def __eq__(self, rhs):
        return self.property == rhs.property and self.value == rhs.value

    def __hash__(self):
        return hash((self.property, self.value))

    def __str__(self):
        return f'{self.property}: {self.value}'

    def __jsonout__(self):
        if(type(self.value) == str):
            value_out = self.value
        else:
            value_out = self.value.__jsonout__()
        return {
                   "snaktype": "value",
                   "property": self.property,
                   "datatype": tfsl.utils.values_datatype(self.property),
                   "datavalue": {
                       "value": value_out,
                       "type": tfsl.utils.values_type(self.property)
                   }
               }


def build_value(value_in):
    value_type = value_in["type"]
    actual_value = value_in["value"]
    if(value_type == "string"):
        return actual_value
    elif(value_type == "wikibase-entityid"):
        return tfsl.itemvalue.build_itemvalue(actual_value)
    elif(value_type == "monolingualtext"):
        return tfsl.monolingualtext.build_mtvalue(actual_value)
    elif(value_type == "globecoordinate"):  # TODO
        return tfsl.coordinatevalue.build_coordinatevalue(actual_value)
    elif(value_type == "quantity"):  # TODO
        return tfsl.quantityvalue.build_quantityvalue(actual_value)
    elif(value_type == "time"):  # TODO
        return tfsl.timevalue.build_timevalue(actual_value)
    else:
        raise ValueError("Type "+value_type+" is not supported yet!")


def build_claim(claim_in):
    claim_prop = claim_in["property"]
    claim_value = build_value(claim_in["datavalue"])

    claim_out = Claim(claim_prop, claim_value)
    claim_out.snaktype = claim_in["snaktype"]
    claim_out.hash = claim_in["hash"]
    claim_out.datatype = claim_in["datatype"]
    return claim_out
