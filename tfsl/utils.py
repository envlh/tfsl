""" Miscellaneous utility functions. """

from copy import deepcopy
from functools import lru_cache
from typing import Any, List, TypeVar

import tfsl.auth
import tfsl.interfaces as I

DEFAULT_INDENT = "    "
WD_PREFIX = "http://www.wikidata.org/entity/"

def prefix_wd(arg: str) -> str:
    """ Removes the entity prefix from the provided string. """
    return WD_PREFIX + arg

def strip_prefix_wd(arg: str) -> str:
    """ Removes the entity prefix from the provided string. """
    if arg.startswith(WD_PREFIX):
        return arg[len(WD_PREFIX):]
    return arg

ListT = TypeVar('ListT')
def add_to_list(references: List[ListT], arg: ListT) -> List[ListT]:
    """ Adds a ListT to a list of ListTs. """
    newreferences = deepcopy(references)
    newreferences.append(arg)
    return newreferences

def sub_from_list(references: List[ListT], arg: ListT) -> List[ListT]:
    """ Removes a ListT from a list of ListTs. """
    newreferences = deepcopy(references)
    newreferences = [reference for reference in newreferences if reference != arg]
    return newreferences

external_to_internal_type_mapping = {
    "commonsMedia": "string",
    "entity-schema": "string",
    "external-id": "string",
    "geo-shape": "string",
    "globe-coordinate": "globecoordinate",
    "monolingualtext": "monolingualtext",
    "quantity": "quantity",
    "string": "string",
    "tabular-data": "string",
    "time": "time",
    "url": "string",
    "wikibase-item": "wikibase-entityid",
    "wikibase-property": "wikibase-entityid",
    "math": "string",
    "wikibase-lexeme": "wikibase-entityid",
    "wikibase-form": "wikibase-entityid",
    "wikibase-sense": "wikibase-entityid",
    "musical-notation": "string"
}

@lru_cache
def values_type(prop: I.Pid) -> str:
    """ Returns the internal datatype of the provided property. """
    return external_to_internal_type_mapping[values_datatype(prop)]

@lru_cache
def values_datatype(prop: I.Pid) -> str:
    """ Returns the outward-facing datatype of the provided property. """
    prop_data = tfsl.auth.retrieve_single_entity(prop)
    if I.is_PropertyDict(prop_data):
        return prop_data["datatype"]
    raise ValueError(f'Attempting to get datatype of non-property {prop}')

def is_novalue(value: Any) -> bool:
    """ Checks that a value is a novalue. """
    return value is False

def is_somevalue(value: Any) -> bool:
    """ Checks that a value is a somevalue. """
    return value is True
