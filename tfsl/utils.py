from copy import deepcopy
from functools import singledispatch
from json import JSONEncoder
import re

import requests

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

def find_lexeme(lemma, language, category):
    # TODO: have a method in lexeme.py that returns each lexeme from the result list?
    # TODO: make the query customizable?
    query_in = f'SELECT ?i {{ ?i dct:language wd:{language.item} ; wikibase:lemma "{lemma.text}"@{lemma.language.code} ; wikibase:lexicalCategory wd:{category} }}'
    query_url = "https://query.wikidata.org/sparql"
    query_parameters = {
        "query": query_in
    }
    query_headers = {
        "Accept": "application/sparql-results+json"
    }
    R = requests.post(query_url, data=query_parameters, headers=query_headers)
    if R.status_code != 200:
        raise Exception("POST was unsuccessfull ({}): {}".format(R.status_code, R.text))

    query_out = R.json()
    return [binding["i"]["value"].replace('http://www.wikidata.org/entity/','') for binding in query_out["results"]["bindings"]]
