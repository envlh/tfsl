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

    def __add__(self, arg):
        return Statement(self.property, self.value) + arg
    
    def __matmul__(self, arg):
        return Statement(self.property, self.value) @ arg

    def __jsonout__(self):
        return {
                   "snaktype": "value",
                   "property": self.property,
                   "datatype": tfsl.utils.values_datatype(self.property),
                   "datavalue": {
                       "value": self.value.__jsonout__,
                       "type": tfsl.utils.values_type(self.property)
                   }
               }
