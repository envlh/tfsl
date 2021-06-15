from functools import singledispatchmethod
import json

import tfsl.languages
import tfsl.utils


class ItemValue:
    """ Representation of a Wikibase entity of some sort.
    """
    def __init__(self, item_id: str):
        self.item_id = item_id
        if(tfsl.utils.matches_item(item_id)):
            self.item_type = 'item'
        elif(tfsl.utils.matches_property(item_id)):
            self.item_type = 'property'
        elif(tfsl.utils.matches_lexeme(item_id)):
            self.item_type = 'lexeme'
        elif(tfsl.utils.matches_form(item_id)):
            self.item_type = 'form'
        elif(tfsl.utils.matches_sense(item_id)):
            self.item_type = 'sense'

    def __eq__(self, rhs):
        return self.item_id == rhs.item_id and self.item_type == rhs.item_type

    def __hash__(self):
        return hash((self.item_type, self.item_id))

    def __str__(self):
        return f'{self.item_id}'

    def __jsonout__(self):
        base_dict = {
                   "entity-type": self.item_type,
                   "id": self.item_id
               }
        if(self.item_type in ['item', 'property', 'lexeme']):
            base_dict["numeric-id"] = int(self.item_id[1:])
        return base_dict


def build_itemvalue(value_in):
    return ItemValue(value_in["id"])
