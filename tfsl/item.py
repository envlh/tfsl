import json
import os
import os.path
import time
from collections import defaultdict
from copy import deepcopy

import tfsl.auth
import tfsl.languages
import tfsl.lexemeform
import tfsl.lexemesense
import tfsl.monolingualtext
import tfsl.statement
import tfsl.utils

default_item_cache_path = os.path.expanduser('~/.cache/tfsl')
os.makedirs(default_item_cache_path,exist_ok=True)

class Item:
    # TODO: better processing of labels/descriptions/aliases arguments
    def __init__(self, labels=None, descriptions=None, aliases=None, statements=None, sitelinks=None):
        if labels is None:
            self.labels = {}
        else:
            self.labels = labels if isinstance(labels, dict) else dict(labels)

        if descriptions is None:
            self.descriptions = {}
        else:
            self.descriptions = descriptions if isinstance(descriptions, dict) else dict(descriptions)

        if aliases is None:
            self.aliases = {}
        else:
            self.aliases = aliases if isinstance(aliases, dict) else dict(aliases)

        if statements is None:
            self.statements = []
        elif isinstance(statements, list):
            self.statements = defaultdict(list)
            for arg in statements:
                self.statements[arg.property].append(arg)
        else:
            self.statements = deepcopy(statements)

        if sitelinks is None:
            self.sitelinks = {}
        else:
            self.sitelinks = sitelinks if isinstance(sitelinks, dict) else dict(sitelinks)

        self.pageid = None
        self.namespace = None
        self.title = None
        self.lastrevid = None
        self.modified = None
        self.item_type = None
        self.item_id = None

    def set_published_settings(self, item_in):
        self.pageid = item_in["pageid"]
        self.namespace = item_in["ns"]
        self.title = item_in["title"]
        self.lastrevid = item_in["lastrevid"]
        self.modified = item_in["modified"]
        self.item_type = item_in["type"]
        self.item_id = item_in["id"]

def build_item(item_in):
    labels = {}
    for _, label in item_in["labels"].items():
        new_label = label["value"]# @ tfsl.languages.get_first_lang(label["language"])
        labels[label["language"]] = new_label

    descriptions = {}
    for _, description in item_in["descriptions"].items():
        new_description = description["value"]# @ tfsl.languages.get_first_lang(description["language"])
        descriptions[description["language"]] = new_description

    aliases = {}
    for lang, aliaslist in item_in["aliases"].items():
        aliases[lang] = set()
        for alias in aliaslist:
            new_alias = alias["value"]# @ tfsl.languages.get_first_lang(alias["language"])
            aliases[lang].add(new_alias)

    statements_in = item_in["claims"]
    statements = defaultdict(list)
    for prop in statements_in:
        for claim in statements_in[prop]:
            statements[prop].append(tfsl.statement.build_statement(claim))

    sitelinks = item_in["sitelinks"]

    item_out = Item(labels, descriptions, aliases, statements, sitelinks)
    item_out.set_published_settings(item_in)
    return item_out

# pylint: disable=invalid-name

def Q(lid, cache_path=default_item_cache_path, ttl=86400):
    if isinstance(lid, int):
        lid = 'Q'+str(lid)
    filename = os.path.join(cache_path, str(lid)+".json")
    try:
        assert time.time() - os.path.getmtime(filename) < ttl
        with open(filename) as fileptr:
            item_json = json.load(fileptr)
    except (FileNotFoundError, OSError, AssertionError):
        current_lexeme = tfsl.auth.get_lexemes([lid])
        item_json = current_lexeme[lid]
        with open(filename, "w") as fileptr:
            json.dump(item_json, fileptr)
    return build_item(item_json)
