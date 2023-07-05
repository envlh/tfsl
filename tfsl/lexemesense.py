""" Holds the LexemeSense class and a function to build one given a JSON representation of it. """

from functools import singledispatchmethod
from typing import Optional, Protocol, Union, overload

import tfsl.interfaces as I
import tfsl.monolingualtext
import tfsl.monolingualtextholder as MTH
import tfsl.statement
import tfsl.statementholder as STH
import tfsl.utils

class LexemeSenseLike(I.MTST, Protocol):
    """ Defines methods that may be expected when reading from an object representing a Wikibase lexeme sense,
        whether this object is editable (LexemeSense) or not (LS_).
    """
    @property
    def glosses(self) -> MTH.MonolingualTextHolder:
        """ Returns the sense's glosses. """
    @property
    def id(self) -> Optional[str]: # pylint: disable=invalid-name
        """ Returns the sense's LSid. """

class LexemeSense:
    """ Container for a Wikidata lexeme sense. """
    def __init__(self,
                 glosses: Union[MTH.MonolingualTextHolder,
                                tfsl.monolingualtext.MonolingualText,
                                I.MonolingualTextList],
                 statements: Optional[Union[STH.StatementHolder, I.StatementHolderInput]]=None):
        super().__init__()
        if isinstance(glosses, MTH.MonolingualTextHolder):
            self.glosses = glosses
        else:
            self.glosses = MTH.MonolingualTextHolder(glosses)

        if isinstance(statements, STH.StatementHolder):
            self.statements = statements
        else:
            self.statements = STH.StatementHolder(statements)

        self.id: Optional[str] = None # pylint: disable=invalid-name

    def get_published_settings(self) -> I.LexemeSensePublishedSettings:
        """ Returns a dictionary containing those portions of the LexemeSense JSON dictionary
            which are only significant at editing time for existing lexeme senses.
        """
        if self.id is not None:
            return {
                "id": self.id
            }
        return {}

    def set_published_settings(self, sense_in: I.LexemeSensePublishedSettings) -> None:
        """ Sets based on a LexemeSense JSON dictionary those variables
            which are only significant at editing time for existing lexeme senses.
        """
        if "id" in sense_in:
            self.id = sense_in["id"]

    @overload
    def __getitem__(self, arg: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText: ...
    @overload
    def __getitem__(self, arg: tfsl.monolingualtext.MonolingualText) -> tfsl.monolingualtext.MonolingualText: ...
    @overload
    def __getitem__(self, arg: I.Pid) -> I.StatementList: ...
    @overload
    def __getitem__(self, arg: 'tfsl.itemvalue.ItemValue') -> I.StatementList: ...

    def __getitem__(self, arg: object) -> Union[I.StatementList, tfsl.monolingualtext.MonolingualText]:
        if isinstance(arg, str):
            return self.statements[arg]
        elif isinstance(arg, tfsl.itemvalue.ItemValue):
            return self.statements[arg.id]
        elif isinstance(arg, tfsl.languages.Language) or isinstance(arg, tfsl.monolingualtext.MonolingualText):
            return self.glosses[arg]
        raise KeyError(f"Can't get {type(arg)} from LexemeForm")

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return self.statements.haswbstatement(property_in, value_in)

    def __add__(self, arg: object) -> 'LexemeSense':
        if isinstance(arg, tfsl.monolingualtext.MonolingualText):
            published_settings = self.get_published_settings()
            sense_out = LexemeSense(self.glosses + arg, self.statements)
            sense_out.set_published_settings(published_settings)
            return sense_out
        elif isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            sense_out = LexemeSense(self.glosses, self.statements + arg)
            sense_out.set_published_settings(published_settings)
            return sense_out
        raise NotImplementedError(f"Can't add {type(arg)} to LexemeSense")

    def __sub__(self, arg: object) -> 'LexemeSense':
        if isinstance(arg, tfsl.languages.Language) or isinstance(arg, tfsl.monolingualtext.MonolingualText):
            published_settings = self.get_published_settings()
            sense_out = LexemeSense(self.glosses - arg, self.statements)
            sense_out.set_published_settings(published_settings)
            return sense_out
        elif isinstance(arg, str):
            published_settings = self.get_published_settings()
            if I.is_Pid(arg):
                sense_out = LexemeSense(self.glosses, self.statements - arg)
            sense_out.set_published_settings(published_settings)
            return sense_out
        elif isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            sense_out = LexemeSense(self.glosses, self.statements - arg)
            sense_out.set_published_settings(published_settings)
            return sense_out
        raise NotImplementedError(f"Can't subtract {type(arg)} from LexemeSense")

    def __contains__(self, arg: object) -> bool:
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg: object) -> bool:
        """ Dispatches __contains__. """
        raise KeyError(f"Can't check for {type(arg)} in LexemeSense")

    @contains.register(tfsl.languages.Language)
    @contains.register(tfsl.monolingualtext.MonolingualText)
    def _(self, arg: I.LanguageOrMT) -> bool:
        return arg in self.glosses

    @contains.register(tfsl.statement.Statement)
    @contains.register(tfsl.claim.Claim)
    @contains.register(str)
    def _(self, arg: Union[str, tfsl.claim.Claim, tfsl.statement.Statement]) -> bool:
        return arg in self.statements

    def __repr__(self) -> str:
        return f"<{self.id}: {len(self.glosses)} glosses, {len(self.statements)} statements>"

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, LexemeSense):
            return NotImplemented
        glosses_equal = self.glosses == rhs.glosses
        statements_equal = self.statements == rhs.statements
        return glosses_equal and statements_equal

    def __str__(self) -> str:
        gloss_str = str(self.glosses)
        stmt_str = str(self.statements)
        return "\n".join([gloss_str, stmt_str])

    def __jsonout__(self) -> I.LexemeSenseDict:
        glosses_dict = self.glosses.__jsonout__()
        base_dict: I.LexemeSenseDict = {"glosses": glosses_dict}

        if self.id is not None:
            base_dict["id"] = self.id
        else:
            base_dict["add"] = ""

        if (statement_dict := self.statements.__jsonout__()):
            base_dict["claims"] = statement_dict

        return base_dict

def build_sense(sense_in: I.LexemeSenseDict) -> LexemeSense:
    """ Builds a LexemeSense from the JSON dictionary describing it. """
    glosses = MTH.build_text_list(sense_in["glosses"])
    statements = STH.build_statement_list(sense_in["claims"])

    sense_out = LexemeSense(glosses, statements)
    sense_out.id = sense_in["id"]
    return sense_out

class LS_: # pylint: disable=invalid-name
    """ A LexemeSense, but sense glosses are not auto-converted to MonolingualTexts
        and statements are only assembled into Statements when accessed.

        See the documentation of LexemeSenseLike methods for general information about
        what certain methods do.
    """
    def __init__(self, sense_json: I.LexemeSenseDict):
        self.json = sense_json

    @property
    def id(self) -> I.LSid:
        """ (See LexemeSenseLike.id for what this method does.) """
        current_id = self.json["id"]
        if I.is_LSid(current_id):
            return current_id
        raise ValueError("Somehow the sense ID is not a valid sense ID")

    @property
    def glosses(self) -> MTH.MonolingualTextHolder:
        """ (See LexemeSenseLike.glosses for what this method does.) """
        return MTH.MonolingualTextHolder(MTH.build_text_list(self.json["glosses"]))

    def __repr__(self) -> str:
        return f"<{self.id}: {len(self.json['glosses'])} glosses, {sum(len(y) for x, y in self.json['claims'].items())} statements>"

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return STH.haswbstatement(self.json["claims"], property_in, value_in)

    @overload
    def __getitem__(self, arg: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText: ...
    @overload
    def __getitem__(self, arg: tfsl.monolingualtext.MonolingualText) -> tfsl.monolingualtext.MonolingualText: ...
    @overload
    def __getitem__(self, arg: I.Pid) -> I.StatementList: ...
    @overload
    def __getitem__(self, arg: 'tfsl.itemvalue.ItemValue') -> I.StatementList: ...

    def __getitem__(self, arg: object) -> Union[I.StatementList, tfsl.monolingualtext.MonolingualText]:
        if isinstance(arg, str):
            return self.getitem_str(arg)
        elif isinstance(arg, tfsl.itemvalue.ItemValue):
            return self.getitem_str(arg.id)
        elif isinstance(arg, tfsl.languages.Language):
            return MTH.get_lang_from_mtlist(self.json["glosses"], arg)
        elif isinstance(arg, tfsl.monolingualtext.MonolingualText):
            lang = arg.language
            lang_code = lang.code
            return tfsl.monolingualtext.build_lemma(self.json["glosses"][lang_code])
        raise KeyError(f"Can't get {type(arg)} from LexemeSense")

    def getitem_pid(self, key: I.Pid) -> I.StatementList:
        """ :meta private: """
        return self.get_stmts(key)

    def get_stmts(self, prop: I.Pid) -> I.StatementList:
        """ Assembles a list of Statements present on the item with the given property. """
        return [tfsl.statement.build_statement(stmt) for stmt in self.json["claims"].get(prop,[])]

    def getitem_str(self, key: str) -> I.StatementList:
        """ Common handling of __getitem__ for inputs as strings or the ids of ItemValues. """
        if I.is_Pid(key):
            return self.getitem_pid(key)
        raise KeyError
