from copy import deepcopy
from functools import singledispatch
from json import JSONEncoder
import re

default_indent = "    "

# TODO: how best to override these for wikibases with custom prefixes?
def matches_item(arg):
    return re.match(r"^Q\d+$", arg)

def matches_property(arg):
    return re.match(r"^P\d+$", arg)

def matches_lexeme(arg):
    return re.match(r"^L\d+$", arg)

def remove_replang(list_in, lang_in):
    newlist = deepcopy(list_in)
    newlist = [rep for rep in newlist if rep.language != lang_in]
    return newlist

def add_claimlike(qualifiers, arg):
    newqualifiers = deepcopy(qualifiers)
    newqualifiers[arg.property].append(arg)
    return newqualifiers

def add_to_list(references, arg):
    newreferences = deepcopy(references)
    newreferences.append(arg)
    return newreferences

def add_to_mtlist(references, arg):
    newreferences = remove_replang(deepcopy(references), arg.language)
    newreferences.append(arg)
    return newreferences

def sub_property(qualifiers, arg):
    newqualifiers = deepcopy(qualifiers)
    del newqualifiers[arg]
    return newqualifiers

def sub_claimlike(qualifiers, arg):
    newqualifiers = deepcopy(qualifiers)
    newqualifiers[arg.property] = [claim for claim in newqualifiers[arg.property] if claim != arg]
    if(len(newqualifiers[arg.property]) == 0):
        return sub_property(newqualifiers, arg.property)
    return newqualifiers

def sub_from_list(references, arg):
    newreferences = deepcopy(references)
    newreferences = [reference for reference in newreferences if reference != arg]
    return newreferences

def newjsondefault(self, obj):
    return getattr(obj.__class__, "__jsonout__", newjsondefault.default)(obj)

newjsondefault.default = JSONEncoder.default  # Save unmodified default.
JSONEncoder.default = newjsondefault # Replace it.
