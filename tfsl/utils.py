import configparser
import os
import re
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any, List, Match, Optional, Tuple, TypeVar

import requests

import tfsl.interfaces as I

DEFAULT_INDENT = "    "
WD_PREFIX = "http://www.wikidata.org/entity/"

# TODO: how best to override these for wikibases with custom prefixes?
def matches_wikibase_object(arg: str) -> Optional[Match[str]]:
    return re.match(r"^([QPL]\d+$|^L\d+-[FS]\d+)$", arg)

def matches_item(arg: str) -> Optional[Match[str]]:
    return re.match(r"^Q\d+$", arg)

def matches_property(arg: str) -> Optional[Match[str]]:
    return re.match(r"^P\d+$", arg)

def matches_lexeme(arg: str) -> Optional[Match[str]]:
    return re.match(r"^L\d+$", arg)

def matches_form(arg: str) -> Optional[Match[str]]:
    return re.match(r"^(L\d+)-(F\d+)$", arg)

def matches_form_suffix(arg: str) -> Optional[Match[str]]:
    return re.match(r"^F\d+$", arg)

def matches_sense(arg: str) -> Optional[Match[str]]:
    return re.match(r"^(L\d+)-(S\d+)$", arg)

def matches_sense_suffix(arg: str) -> Optional[Match[str]]:
    return re.match(r"^S\d+$", arg)

def prefix_wd(arg: str) -> str:
    return WD_PREFIX + arg

def strip_prefix_wd(arg: str) -> str:
    if arg.startswith(WD_PREFIX):
        return arg[len(WD_PREFIX):]
    return arg

ListT = TypeVar('ListT')
def add_to_list(references: List[ListT], arg: ListT) -> List[ListT]:
    newreferences = deepcopy(references)
    newreferences.append(arg)
    return newreferences

def sub_from_list(references: List[ListT], arg: ListT) -> List[ListT]:
    newreferences = deepcopy(references)
    newreferences = [reference for reference in newreferences if reference != arg]
    return newreferences

@lru_cache
def values_type(prop: str) -> str:
    # TODO: rewrite better and make extensible
    mapping = {
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
    return mapping[values_datatype(prop)]

@lru_cache
def values_datatype(prop: str) -> str:
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
    return value is False

def is_somevalue(value: Any) -> bool:
    return value is True

cache_path, time_to_live = read_config()
os.makedirs(cache_path,exist_ok=True)
