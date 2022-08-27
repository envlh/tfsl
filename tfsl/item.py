""" Holds the Item class and a function to build one given a JSON representation of it. """

import json
import os
import os.path
import time
from typing import Dict, Optional, Set, Union

import tfsl.interfaces as I
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
    """ Container for a Wikidata item. """
    def __init__(self,
                 labels: Optional[Union[tfsl.monolingualtextholder.MonolingualTextHolder, I.MonolingualTextList]]=None,
                 descriptions: Optional[Union[tfsl.monolingualtextholder.MonolingualTextHolder, I.MonolingualTextList]]=None,
                 aliases: Optional[Dict[I.LanguageCode, Set[str]]]=None,
                 statements: Optional[Union[tfsl.statementholder.StatementHolder, I.StatementHolderInput]]=None,
                 sitelinks: Optional[Dict[str, I.SitelinkDict]]=None):
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

        self.pageid: Optional[int] = None
        self.namespace: Optional[int] = None
        self.title: Optional[str] = None
        self.lastrevid: Optional[int] = None
        self.modified: Optional[str] = None
        self.item_type: Optional[str] = None
        self.item_id: Optional[I.Qid] = None

    def get_published_settings(self) -> I.ItemPublishedSettings:
        """ Returns a dictionary containing those portions of the Item JSON dictionary
            which are only significant at editing time for existing items.
        """
        if self.pageid is not None and self.namespace is not None and self.title is not None and self.lastrevid is not None and self.modified is not None and self.item_type is not None and self.item_id is not None:
            return {
                "pageid": self.pageid,
                "ns": self.namespace,
                "title": self.title,
                "lastrevid": self.lastrevid,
                "modified": self.modified,
                "type": self.item_type,
                "id": self.item_id
            }
        return {}

    def set_published_settings(self, item_in: I.ItemPublishedSettings) -> None:
        """ Sets based on an Item JSON dictionary those variables
            which are only significant at editing time for existing items.
        """
        if "pageid" in item_in:
            self.pageid = item_in["pageid"]
            self.namespace = item_in["ns"]
            self.title = item_in["title"]
            self.lastrevid = item_in["lastrevid"]
            self.modified = item_in["modified"]
            self.item_type = item_in["type"]
            self.item_id = item_in["id"]

    def __getitem__(self, key: object) -> I.StatementList:
        if isinstance(key, str):
            if I.is_Pid(key):
                return self.statements[key]
            else:
                raise KeyError
        raise KeyError

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return self.statements.haswbstatement(property_in, value_in)

    def get_label(self, arg: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText:
        """ Returns the label on the Item with the provided language. """
        return self.labels[arg]

    def get_description(self, arg: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText:
        """ Returns the description on the Item with the provided language. """
        return self.descriptions[arg]

    def __add__(self, arg: object) -> 'Item':
        if isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            item_out = Item(self.labels, self.descriptions, self.aliases,
                        self.statements + arg, self.sitelinks)
            item_out.set_published_settings(published_settings)
            return item_out
        elif isinstance(arg, tfsl.monolingualtext.MonolingualText):
            raise NotImplementedError("Adding MonolingualText to Item is ambiguous")
        raise NotImplementedError(f"Can't add {type(arg)} to Item")

    def add_label(self, arg: tfsl.monolingualtext.MonolingualText) -> 'Item':
        """ Adds the provided MonolingualText as a label to the Item,
            overwriting any existing label in that MonolingualText's language.
        """
        published_settings = self.get_published_settings()
        item_out = Item(self.labels + arg, self.descriptions, self.aliases,
                      self.statements, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

    def add_description(self, arg: tfsl.monolingualtext.MonolingualText) -> 'Item':
        """ Adds the provided MonolingualText as a description to the Item,
            overwriting any existing description in that MonolingualText's language.
        """
        published_settings = self.get_published_settings()
        item_out = Item(self.labels, self.descriptions + arg, self.aliases,
                      self.statements, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

    def __sub__(self, arg: object) -> 'Item':
        if isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            item_out = Item(self.labels, self.descriptions, self.aliases,
                        self.statements - arg, self.sitelinks)
            item_out.set_published_settings(published_settings)
            return item_out
        elif isinstance(arg, tfsl.monolingualtext.MonolingualText):
            raise NotImplementedError("Subtracting MonolingualText from Item is ambiguous")
        raise NotImplementedError(f"Can't subtract {type(arg)} from Lexeme")

    def sub_label(self, arg: I.LanguageOrMT) -> 'Item':
        """ Removes the label with the provided language (or the language of the provided
            MonolingualText) from the Item.
        """
        published_settings = self.get_published_settings()
        item_out = Item(self.labels - arg, self.descriptions, self.aliases,
                      self.statements, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

    def sub_description(self, arg: I.LanguageOrMT) -> 'Item':
        """ Removes the description with the provided language (or the language of the provided
            MonolingualText) from the Item.
        """
        published_settings = self.get_published_settings()
        item_out = Item(self.labels, self.descriptions - arg, self.aliases,
                      self.statements, self.sitelinks)
        item_out.set_published_settings(published_settings)
        return item_out

def build_item(item_in: I.ItemDict) -> Item:
    """ Builds an Item from the JSON dictionary describing it. """
    labels = tfsl.monolingualtextholder.build_text_list(item_in["labels"])
    descriptions = tfsl.monolingualtextholder.build_text_list(item_in["descriptions"])
    statements = tfsl.statementholder.build_statement_list(item_in["claims"])

    aliases: Dict[I.LanguageCode, Set[str]] = {}
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

def retrieve_item_json(lid_in: Union[int, I.Qid]) -> I.ItemDict:
    """ Retrieves the JSON for the item with the given Qid. """
    lid: I.Qid
    if isinstance(lid_in, int):
        lid = I.Qid('Q'+str(lid_in))
    elif I.is_Qid(lid_in):
        lid = lid_in
    filename = tfsl.utils.get_filename(lid)
    item_json: I.ItemDict
    try:
        assert time.time() - os.path.getmtime(filename) < tfsl.utils.time_to_live
        with open(filename, encoding="utf-8") as fileptr:
            item_json = json.load(fileptr)
    except (FileNotFoundError, OSError, AssertionError) as e:
        current_lexeme = tfsl.auth.get_lexemes([lid])
        current_lid_output = current_lexeme[lid]
        if I.is_ItemDict(current_lid_output):
            item_json = current_lid_output
        else:
            raise ValueError(f"Retrieved entity {lid} was not an item") from e
        with open(filename, "w", encoding="utf-8") as fileptr:
            json.dump(item_json, fileptr)
    return item_json

def Q(qid: Union[int, I.Qid]) -> Item:
    """ Retrieves and returns the item with the provided Qid. """
    item_json = retrieve_item_json(qid)
    return build_item(item_json)

class Q_:
    """ An Item, but labels/descriptions are not auto-converted to MonolingualTexts
        and statements are only assembled into Statements when accessed.
    """
    def __init__(self, input_arg: I.Qid):
        self.item_json: I.ItemDict = retrieve_item_json(input_arg)

    def get_label(self, lang: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText:
        """ Assembles a MonolingualText containing the label with the given language code. """
        label_dict: I.LemmaDict = self.item_json["labels"][lang.code]
        return label_dict["value"] @ lang

    def get_description(self, lang: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText:
        """ Assembles a MonolingualText containing the description with the given language code. """
        description_dict: I.LemmaDict = self.item_json["descriptions"][lang.code]
        return description_dict["value"] @ lang

    def get_stmts(self, prop: I.Pid) -> I.StatementList:
        """ Assembles a list of Statements present on the item with the given property. """
        return [tfsl.statement.build_statement(stmt) for stmt in self.item_json["claims"].get(prop,[])]

    def __getitem__(self, prop: I.Pid) -> I.StatementList:
        return self.get_stmts(prop)
