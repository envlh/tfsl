""" Holder of the ItemValue class and a function to build one given a JSON representation of it. """

from typing import Optional
from typing_extensions import TypeGuard

import tfsl.interfaces as I

class ItemValue:
    """ Representation of a Wikibase entity of some sort. """
    def __init__(self, item_id: I.EntityId):
        self.type: str
        self.id: I.EntityId
        if I.is_Qid(item_id):
            self.type = 'item'
            self.id = I.Qid(item_id)
        elif I.is_Pid(item_id):
            self.type = 'property'
            self.id = I.Pid(item_id)
        elif I.is_Lid(item_id):
            self.type = 'lexeme'
            self.id = I.Lid(item_id)
        elif I.is_LFid(item_id):
            self.type = 'form'
            self.id = I.LFid(item_id)
        elif I.is_LSid(item_id):
            self.type = 'sense'
            self.id = I.LSid(item_id)

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

    def get_Qid(self, otherwise: Optional[I.Qid]=None) -> I.Qid:
        if I.is_Qid(self.id):
            return self.id
        elif otherwise is not None:
            return otherwise
        raise TypeError(f"{self.id} is not an LFid")

    def get_LFid(self, otherwise: Optional[I.LFid]=None) -> I.LFid:
        if I.is_LFid(self.id):
            return self.id
        elif otherwise is not None:
            return otherwise
        raise TypeError(f"{self.id} is not an LFid")

    def get_LSid(self, otherwise: Optional[I.LSid]=None) -> I.LSid:
        if I.is_LSid(self.id):
            return self.id
        elif otherwise is not None:
            return otherwise
        raise TypeError(f"{self.id} is not an LFid")

def is_itemvalue(value_in: I.ClaimDictValueDictionary) -> TypeGuard[I.ItemValueDict]:
    """ Checks that the keys expected for an ItemValue exist. """
    return all(key in value_in for key in ["entity-type", "id"])

def build_itemvalue(value_in: I.ItemValueDict) -> ItemValue:
    """ Builds an ItemValue given the Wikibase JSON for one. """
    return ItemValue(value_in["id"])
