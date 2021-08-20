from functools import singledispatchmethod
import json

import tfsl.languages
import tfsl.utils


class ItemValue:
    """ Representation of a Wikibase entity of some sort.
    """
    def __init__(self, item_id: str):
        self.id = item_id
        if(tfsl.utils.matches_item(item_id)):
            self.type = 'item'
        elif(tfsl.utils.matches_property(item_id)):
            self.type = 'property'
        elif(tfsl.utils.matches_lexeme(item_id)):
            self.type = 'lexeme'
        elif(tfsl.utils.matches_form(item_id)):
            self.type = 'form'
        elif(tfsl.utils.matches_sense(item_id)):
            self.type = 'sense'

    def __eq__(self, rhs):
        if isinstance(rhs, str):
            return self.id == rhs
        return self.id == rhs.id and self.type == rhs.type

    def __hash__(self):
        return hash((self.type, self.id))

    def __str__(self):
        return f'{self.id}'

    def __jsonout__(self):
        base_dict = {
                   "entity-type": self.type,
                   "id": self.id
               }
        if(self.type in ['item', 'property', 'lexeme']):
            base_dict["numeric-id"] = int(self.id[1:])
        return base_dict


def build_itemvalue(value_in):
    return ItemValue(value_in["id"])
