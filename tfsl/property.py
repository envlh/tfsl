""" Holds the Property class and a function to build one given a JSON representation of it. """

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

class Property:
    """ Container for a Wikidata property. """
    def __init__(self,
                 datatype: str,
                 labels: Optional[Union[tfsl.monolingualtextholder.MonolingualTextHolder, I.MonolingualTextList]]=None,
                 descriptions: Optional[Union[tfsl.monolingualtextholder.MonolingualTextHolder, I.MonolingualTextList]]=None,
                 aliases: Optional[Dict[I.LanguageCode, Set[str]]]=None,
                 statements: Optional[Union[tfsl.statementholder.StatementHolder, I.StatementHolderInput]]=None):
        super().__init__()

        self.datatype = datatype

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

        self.pageid: Optional[int] = None
        self.namespace: Optional[int] = None
        self.title: Optional[str] = None
        self.lastrevid: Optional[int] = None
        self.modified: Optional[str] = None
        self.type: Optional[str] = None
        self.id: Optional[I.Pid] = None # pylint: disable=invalid-name

    def get_published_settings(self) -> I.PropertyPublishedSettings:
        """ Returns a dictionary containing those portions of the Property JSON dictionary
            which are only significant at editing time for existing properties.
        """
        if self.pageid is not None and self.namespace is not None and self.title is not None and self.lastrevid is not None and self.modified is not None and self.type is not None and self.id is not None:
            return {
                "pageid": self.pageid,
                "ns": self.namespace,
                "title": self.title,
                "lastrevid": self.lastrevid,
                "modified": self.modified,
                "type": self.type,
                "id": self.id
            }
        return {}

    def set_published_settings(self, property_in: I.PropertyPublishedSettings) -> None:
        """ Sets based on an Property JSON dictionary those variables
            which are only significant at editing time for existing properties.
        """
        if "pageid" in property_in:
            self.pageid = property_in["pageid"]
            self.namespace = property_in["ns"]
            self.title = property_in["title"]
            self.lastrevid = property_in["lastrevid"]
            self.modified = property_in["modified"]
            self.type = property_in["type"]
            self.id = property_in["id"]

    def __getitem__(self, key: object) -> I.StatementList:
        if isinstance(key, str):
            if I.is_Pid(key):
                return self.statements[key]
            else:
                raise KeyError
        raise KeyError

    def __str__(self) -> str:
        remainder = f"{len(self.labels)}/{len(self.descriptions)}, {len(self.statements)}"
        if self.id:
            return "{"+self.id+": "+remainder+"}"
        return "{Property: "+remainder+"}"

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return self.statements.haswbstatement(property_in, value_in)

    def get_label(self, arg: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText:
        """ Returns the label on the Property with the provided language. """
        return self.labels[arg]

    def get_description(self, arg: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText:
        """ Returns the description on the Property with the provided language. """
        return self.descriptions[arg]

    def __add__(self, arg: object) -> 'Property':
        if isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            property_out = Property(self.datatype, self.labels, self.descriptions, self.aliases,
                        self.statements + arg)
            property_out.set_published_settings(published_settings)
            return property_out
        elif isinstance(arg, tfsl.monolingualtext.MonolingualText):
            raise NotImplementedError("Adding MonolingualText to Property is ambiguous")
        raise NotImplementedError(f"Can't add {type(arg)} to Property")

    def add_label(self, arg: tfsl.monolingualtext.MonolingualText) -> 'Property':
        """ Adds the provided MonolingualText as a label to the Property,
            overwriting any existing label in that MonolingualText's language.
        """
        published_settings = self.get_published_settings()
        property_out = Property(self.datatype, self.labels + arg, self.descriptions, self.aliases,
                      self.statements)
        property_out.set_published_settings(published_settings)
        return property_out

    def add_description(self, arg: tfsl.monolingualtext.MonolingualText) -> 'Property':
        """ Adds the provided MonolingualText as a description to the Property,
            overwriting any existing description in that MonolingualText's language.
        """
        published_settings = self.get_published_settings()
        property_out = Property(self.datatype, self.labels, self.descriptions + arg, self.aliases,
                      self.statements)
        property_out.set_published_settings(published_settings)
        return property_out

    def __sub__(self, arg: object) -> 'Property':
        if isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            property_out = Property(self.datatype, self.labels, self.descriptions, self.aliases,
                        self.statements - arg)
            property_out.set_published_settings(published_settings)
            return property_out
        elif isinstance(arg, tfsl.monolingualtext.MonolingualText):
            raise NotImplementedError("Subtracting MonolingualText from Property is ambiguous")
        raise NotImplementedError(f"Can't subtract {type(arg)} from Lexeme")

    def sub_label(self, arg: I.LanguageOrMT) -> 'Property':
        """ Removes the label with the provided language (or the language of the provided
            MonolingualText) from the Property.
        """
        published_settings = self.get_published_settings()
        property_out = Property(self.datatype, self.labels - arg, self.descriptions, self.aliases,
                      self.statements)
        property_out.set_published_settings(published_settings)
        return property_out

    def sub_description(self, arg: I.LanguageOrMT) -> 'Property':
        """ Removes the description with the provided language (or the language of the provided
            MonolingualText) from the Property.
        """
        published_settings = self.get_published_settings()
        property_out = Property(self.datatype, self.labels, self.descriptions - arg, self.aliases,
                      self.statements)
        property_out.set_published_settings(published_settings)
        return property_out

def build_property(property_in: I.PropertyDict) -> Property:
    """ Builds a Property from the JSON dictionary describing it. """
    labels = tfsl.monolingualtextholder.build_text_list(property_in["labels"])
    descriptions = tfsl.monolingualtextholder.build_text_list(property_in["descriptions"])
    statements = tfsl.statementholder.build_statement_list(property_in["claims"])

    aliases: Dict[I.LanguageCode, Set[str]] = {}
    for lang, aliaslist in property_in["aliases"].items():
        aliases[lang] = set()
        for alias in aliaslist:
            new_alias = alias["value"]# @ tfsl.languages.get_first_lang(alias["language"])
            aliases[lang].add(new_alias)

    property_out = Property(property_in["datatype"], labels, descriptions, aliases, statements)
    property_out.set_published_settings(property_in)
    return property_out

def retrieve_property_json(pid_in: Union[int, I.Pid]) -> I.PropertyDict:
    """ Retrieves the JSON for the property with the given Pid. """
    pid = I.get_Pid_string(pid_in)
    property_dict = tfsl.auth.retrieve_single_entity(pid)
    if I.is_PropertyDict(property_dict):
        return property_dict
    raise ValueError(f'Returned JSON for {pid_in} is not a property')

def P(pid: Union[int, I.Pid]) -> Property: # pylint: disable=invalid-name
    """ Retrieves and returns the property with the provided Qid. """
    property_json = retrieve_property_json(pid)
    return build_property(property_json)

class P_: # pylint: disable=invalid-name
    """ A Property, but labels/descriptions are not auto-converted to MonolingualTexts
        and statements are only assembled into Statements when accessed.
    """
    def __init__(self, input_arg: I.Pid):
        self.property_json: I.PropertyDict = retrieve_property_json(input_arg)

    def get_label(self, lang: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText:
        """ Assembles a MonolingualText containing the label with the given language code. """
        label_dict: I.LemmaDict = self.property_json["labels"][lang.code]
        return label_dict["value"] @ lang

    def get_description(self, lang: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText:
        """ Assembles a MonolingualText containing the description with the given language code. """
        description_dict: I.LemmaDict = self.property_json["descriptions"][lang.code]
        return description_dict["value"] @ lang

    def get_stmts(self, prop: I.Pid) -> I.StatementList:
        """ Assembles a list of Statements present on the property with the given property. """
        return [tfsl.statement.build_statement(stmt) for stmt in self.property_json["claims"].get(prop,[])]

    def __getitem__(self, prop: I.Pid) -> I.StatementList:
        return self.get_stmts(prop)
