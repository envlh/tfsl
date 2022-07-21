""" Holder of the ItemValue class and a function to build one given a JSON representation of it. """

from typing_extensions import TypeGuard

import tfsl.interfaces as I

class ItemValue:
    """ Representation of a Wikibase entity of some sort. """
    def __init__(self, item_id: I.EntityId):
        self.id = item_id
        self.type: str
        if I.is_Qid(item_id):
            self.type = 'item'
        elif I.is_Pid(item_id):
            self.type = 'property'
        elif I.is_Lid(item_id):
            self.type = 'lexeme'
        elif I.is_LFid(item_id):
            self.type = 'form'
        elif I.is_LSid(item_id):
            self.type = 'sense'

    def __eq__(self, rhs: object) -> bool:
        if isinstance(rhs, str):
            return self.id == rhs
        elif not isinstance(rhs, ItemValue):
            return NotImplemented
        return self.id == rhs.id and self.type == rhs.type

    def __hash__(self) -> int:
        return hash((self.type, self.id))

    def __str__(self) -> str:
        return f'{self.id}'

    def __jsonout__(self) -> I.ItemValueDict:
        base_dict: I.ItemValueDict = {
            "entity-type": self.type,
            "id": self.id
        }
        if(self.type in ['item', 'property', 'lexeme']):
            base_dict["numeric-id"] = int(self.id[1:])
        return base_dict

def is_itemvalue(value_in: I.ClaimDictValueDictionary) -> TypeGuard[I.ItemValueDict]:
    """ Checks that the keys expected for an ItemValue exist. """
    return all(key in value_in for key in ["entity-type", "id"])

def build_itemvalue(value_in: I.ItemValueDict) -> ItemValue:
    """ Builds an ItemValue given the Wikibase JSON for one. """
    return ItemValue(value_in["id"])
