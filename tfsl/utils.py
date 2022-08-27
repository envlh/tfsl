""" Miscellaneous utility functions. """

import configparser
import os
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any, List, Match, Optional, Tuple, TypeVar

import requests

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
def values_type(prop: str) -> str:
    """ Returns the internal datatype of the provided property. """
    return external_to_internal_type_mapping[values_datatype(prop)]

@lru_cache
def values_datatype(prop: str) -> str:
    """ Returns the outward-facing datatype of the provided property. """
    # TODO: rewrite better
    prop_response = requests.get('https://www.wikidata.org/wiki/Special:EntityData/'+prop+'.json')
    prop_response_json = prop_response.json()
    if isinstance(prop_response_json, dict):
        prop_data: I.PropertyDict = prop_response_json["entities"][prop]
        return prop_data["datatype"]
    raise ValueError(f"Response from retrieving {prop} not valid JSON")

def read_config() -> Tuple[str, float]:
    """ Reads the config file residing at /path/to/tfsl/config.ini. """
    config = configparser.ConfigParser()
    current_config_path = (Path(__file__).parent / '../config.ini').resolve()
    config.read(current_config_path)
    cpath = config['Tfsl']['CachePath']
    ttl = float(config['Tfsl']['TimeToLive'])
    return cpath, ttl

def get_filename(entity_name: str) -> str:
    """ Constructs the name of a text file containing a sense subgraph based on a given property. """
    return os.path.join(cache_path, f"{entity_name}.json")

def is_novalue(value: Any) -> bool:
    """ Checks that a value is a novalue. """
    return value is False

def is_somevalue(value: Any) -> bool:
    """ Checks that a value is a somevalue. """
    return value is True

cache_path, time_to_live = read_config()
os.makedirs(cache_path,exist_ok=True)
