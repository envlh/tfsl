import json
import os
import os.path
import time
from collections import defaultdict
from copy import deepcopy
from functools import singledispatchmethod

import tfsl.auth
import tfsl.languages
import tfsl.lexemeform
import tfsl.lexemesense
import tfsl.monolingualtext
import tfsl.monolingualtextholder
import tfsl.statement
import tfsl.statementholder
import tfsl.utils

default_item_cache_path = os.path.expanduser('~/.cache/tfsl')
os.makedirs(default_item_cache_path,exist_ok=True)

class Item:
    # TODO: better processing of labels/descriptions/aliases arguments
    def __init__(self, labels=None, descriptions=None, aliases=None, statements=None, sitelinks=None):
        super().__init__()
        if isinstance(labels, tfsl.monolingualtextholder.MonolingualTextHolder):
            self.labels = labels
        else:
            self.labels = tfsl.monolingualtextholder.MonolingualTextHolder(labels)

        if isinstance(descriptions, tfsl.monolingualtextholder.MonolingualTextHolder):
            self.descriptions = descriptions
        else:
            self.descriptions = tfsl.monolingualtextholder.MonolingualTextHolder(descriptions)

        if aliases is None:
            self.aliases = {}
        else:
            self.aliases = aliases if isinstance(aliases, dict) else dict(aliases)

        if isinstance(statements, tfsl.statementholder.StatementHolder):
            self.statements = statements
        else:
            self.statements = tfsl.statementholder.StatementHolder(statements)

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

    def __getitem__(self, key):
        id_matches_key = lambda obj: obj.id == key

        if tfsl.utils.matches_property(key):
            return self.statements[key]
        raise KeyError

    def get_published_settings(self):
        return {
            "pageid": self.pageid,
            "ns": self.namespace,
            "title": self.title,
            "lastrevid": self.lastrevid,
            "modified": self.modified,
            "type": self.item_type,
            "id": self.item_id
        }

    def set_published_settings(self, item_in):
        self.pageid = item_in["pageid"]
        self.namespace = item_in["ns"]
        self.title = item_in["title"]
        self.lastrevid = item_in["lastrevid"]
        self.modified = item_in["modified"]
        self.item_type = item_in["type"]
        self.item_id = item_in["id"]

    def __add__(self, arg):
        return self.add(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {type(arg)} to Lexeme")

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        published_settings = self.get_published_settings()
        item_out = Item(self.labels, self.descriptions, self.aliases,
                      self.statements + arg, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

    @add.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        raise NotImplementedError(f"Adding MonolingualText to Item is ambiguous")

    def add_label(self, arg: tfsl.monolingualtext.MonolingualText):
        published_settings = self.get_published_settings()
        item_out = Item(self.labels + arg, self.descriptions, self.aliases,
                      self.statements, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

    def add_description(self, arg: tfsl.monolingualtext.MonolingualText):
        published_settings = self.get_published_settings()
        item_out = Item(self.labels, self.descriptions + arg, self.aliases,
                      self.statements, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

    def __sub__(self, arg):
        return self.sub(arg)

    @singledispatchmethod
    def sub(self, arg):
        raise NotImplementedError(f"Can't subtract {type(arg)} from Lexeme")

    @sub.register
    def _(self, arg: tfsl.statement.Statement):
        published_settings = self.get_published_settings()
        item_out = Item(self.labels, self.descriptions, self.aliases,
                      self.statements - arg, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

    @sub.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        raise NotImplementedError(f"Subtracting MonolingualText from Item is ambiguous")

    def sub_label(self, arg: tfsl.monolingualtextholder.lang_or_mt):
        published_settings = self.get_published_settings()
        item_out = Item(self.labels - arg, self.descriptions, self.aliases,
                      self.statements, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

    def sub_description(self, arg: tfsl.monolingualtextholder.lang_or_mt):
        published_settings = self.get_published_settings()
        item_out = Item(self.labels, self.descriptions - arg, self.aliases,
                      self.statements, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

def build_item(item_in):
    labels = tfsl.monolingualtextholder.build_text_list(item_in["labels"])
    descriptions = tfsl.monolingualtextholder.build_text_list(item_in["descriptions"])
    statements = tfsl.statementholder.build_statement_list(item_in["claims"])

    aliases = {}
    for lang, aliaslist in item_in["aliases"].items():
        aliases[lang] = set()
        for alias in aliaslist:
            new_alias = alias["value"]# @ tfsl.languages.get_first_lang(alias["language"])
            aliases[lang].add(new_alias)

    sitelinks = item_in["sitelinks"]

    item_out = Item(labels, descriptions, aliases, statements, sitelinks)
    item_out.set_published_settings(item_in)
    return item_out

# pylint: disable=invalid-name

def Q(lid):
    if isinstance(lid, int):
        lid = 'Q'+str(lid)
    filename = tfsl.utils.get_filename(lid)
    try:
        assert time.time() - os.path.getmtime(filename) < tfsl.utils.time_to_live
        with open(filename) as fileptr:
            item_json = json.load(fileptr)
    except (FileNotFoundError, OSError, AssertionError):
        current_lexeme = tfsl.auth.get_lexemes([lid])
        item_json = current_lexeme[lid]
        with open(filename, "w") as fileptr:
            json.dump(item_json, fileptr)
    return build_item(item_json)
