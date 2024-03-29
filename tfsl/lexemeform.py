""" Holds the LexemeForm class and a function to build one given a JSON representation of it. """

from functools import singledispatchmethod
from typing import Collection, List, Optional, Protocol, Set, Union, overload

import tfsl.interfaces as I
import tfsl.languages
import tfsl.monolingualtext
import tfsl.monolingualtextholder as MTH
import tfsl.statement
import tfsl.statementholder as STH
import tfsl.utils

class LexemeFormLike(I.MTST, Protocol):
    """ Defines methods that may be expected when reading from an object representing a Wikibase lexeme form,
        whether this object is editable (LexemeForm) or not (LF_).
    """
    @property
    def features(self) -> Collection[I.Qid]:
        """ Returns the form's grammatical features. """
    @property
    def representations(self) -> MTH.MonolingualTextHolder:
        """ Returns the form's representations. """
    @property
    def id(self) -> Optional[str]: # pylint: disable=invalid-name
        """ Returns the form's LFid. """

class LexemeForm:
    """ Container for a Wikidata lexeme form.

        See the documentation of LexemeFormLike methods for general information about
        what certain methods do.
    """
    def __init__(self,
                 representations: Union[MTH.MonolingualTextHolder,
                                        tfsl.monolingualtext.MonolingualText,
                                        I.MonolingualTextList],
                 features: Optional[Union[List[I.Qid], Set[I.Qid]]]=None,
                 statements: Optional[Union[STH.StatementHolder, I.StatementHolderInput]]=None):
        super().__init__()

        self.representations: MTH.MonolingualTextHolder
        if isinstance(representations, MTH.MonolingualTextHolder):
            self.representations = representations
        else:
            self.representations = MTH.MonolingualTextHolder(representations)

        if isinstance(statements, STH.StatementHolder):
            self.statements = statements
        else:
            self.statements = STH.StatementHolder(statements)

        self.features: Set[I.Qid]
        if features is None:
            self.features = set()
        else:
            self.features = set(features)

        self.id: Optional[str] = None # pylint: disable=invalid-name

    def get_published_settings(self) -> I.LexemeFormPublishedSettings:
        """ Returns a dictionary containing those portions of the LexemeForm JSON dictionary
            which are only significant at editing time for existing lexeme forms.
        """
        if self.id is not None:
            return {
                "id": self.id
            }
        return {}

    def set_published_settings(self, form_in: I.LexemeFormPublishedSettings) -> None:
        """ Sets based on a LexemeForm JSON dictionary those variables
            which are only significant at editing time for existing lexeme forms.
        """
        if "id" in form_in:
            self.id = form_in["id"]

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
            return self.representations[arg]
        raise KeyError(f"Can't get {type(arg)} from LexemeForm")

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return self.statements.haswbstatement(property_in, value_in)

    def __add__(self, arg: object) -> 'LexemeForm':
        if isinstance(arg, tfsl.monolingualtext.MonolingualText):
            published_settings = self.get_published_settings()
            form_out = LexemeForm(self.representations + arg, self.features, self.statements)
            form_out.set_published_settings(published_settings)
            return form_out
        elif isinstance(arg, str):
            published_settings = self.get_published_settings()
            if I.is_Qid(arg):
                form_out = LexemeForm(self.representations, self.features | set([arg]), self.statements)
            form_out.set_published_settings(published_settings)
            return form_out
        elif isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            form_out = LexemeForm(self.representations, self.features, self.statements + arg)
            form_out.set_published_settings(published_settings)
            return form_out
        raise NotImplementedError(f"Can't add {type(arg)} to LexemeForm")

    def __sub__(self, arg: object) -> 'LexemeForm':
        if isinstance(arg, tfsl.languages.Language) or isinstance(arg, tfsl.monolingualtext.MonolingualText):
            published_settings = self.get_published_settings()
            form_out = LexemeForm(self.representations - arg, self.features, self.statements)
            form_out.set_published_settings(published_settings)
            return form_out
        elif isinstance(arg, str):
            published_settings = self.get_published_settings()
            if I.is_Qid(arg):
                form_out = LexemeForm(self.representations, self.features - set([arg]), self.statements)
            elif I.is_Pid(arg):
                form_out = LexemeForm(self.representations, self.features, self.statements - arg)
            form_out.set_published_settings(published_settings)
            return form_out
        elif isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            form_out = LexemeForm(self.representations, self.features, self.statements - arg)
            form_out.set_published_settings(published_settings)
            return form_out
        raise NotImplementedError(f"Can't subtract {type(arg)} from LexemeForm")

    def __contains__(self, arg: object) -> bool:
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg: object) -> bool:
        """ Dispatches __contains__. """
        raise KeyError(f"Can't check for {type(arg)} in LexemeForm")

    @contains.register(tfsl.languages.Language)
    @contains.register(tfsl.monolingualtext.MonolingualText)
    def _(self, arg: I.LanguageOrMT) -> bool:
        return arg in self.representations

    @contains.register
    def _(self, arg: tfsl.claim.Claim) -> bool:
        return arg in self.statements

    @contains.register
    def _(self, arg: str) -> bool:
        try:
            return arg in self.statements
        except TypeError as exception:
            if I.is_Qid(arg):
                return arg in self.features
            raise exception

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, LexemeForm):
            return NotImplemented
        representations_equal = self.representations == rhs.representations
        features_equal = self.features == rhs.features
        statements_equal = self.statements == rhs.statements
        return representations_equal and features_equal and statements_equal

    def __str__(self) -> str:
        base_str = str(self.representations)
        feat_str = ': '+', '.join(self.features)
        stmt_str = str(self.statements)
        return "\n".join([base_str + feat_str, stmt_str])

    def __jsonout__(self) -> I.LexemeFormDict:
        reps_dict = self.representations.__jsonout__()
        base_dict: I.LexemeFormDict = {"representations": reps_dict, "grammaticalFeatures": list(self.features)}

        if self.id is not None:
            base_dict["id"] = self.id
        else:
            base_dict["add"] = ""

        if (statement_dict := self.statements.__jsonout__()) is not None:
            base_dict["claims"] = statement_dict

        return base_dict

def build_form(form_in: I.LexemeFormDict) -> LexemeForm:
    """ Builds a LexemeForm from the JSON dictionary describing it. """
    reps = MTH.build_text_list(form_in["representations"])
    feats = form_in["grammaticalFeatures"]
    claims = STH.build_statement_list(form_in["claims"])

    form_out = LexemeForm(reps, feats, claims)
    form_out.set_published_settings(form_in)

    return form_out

class LF_: # pylint: disable=invalid-name
    """ A LexemeForm, but form representations are not auto-converted to MonolingualTexts
        and statements are only assembled into Statements when accessed.

        See the documentation of LexemeLike methods for general information about
        what certain methods do.
    """
    def __init__(self, form_json: I.LexemeFormDict):
        self.json = form_json

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return STH.haswbstatement(self.json["claims"], property_in, value_in)

    @property
    def features(self) -> List[I.Qid]:
        """ (See LexemeFormLike.features for what this method does.) """
        return self.json["grammaticalFeatures"]

    @property
    def representations(self) -> MTH.MonolingualTextHolder:
        """ (See LexemeFormLike.representations for what this method does.) """
        return MTH.MonolingualTextHolder(MTH.build_text_list(self.json["representations"]))

    @property
    def id(self) -> str:
        """ (See LexemeFormLike.id for what this method does.) """
        return self.json["id"]

    def __repr__(self) -> str:
        return f"<{self.id}: {len(self.json['representations'])} reps, {len(self.json['grammaticalFeatures'])} features, {sum(len(y) for x, y in self.json['claims'].items())} statements>"

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
            return MTH.get_lang_from_mtlist(self.json["representations"], arg)
        elif isinstance(arg, tfsl.monolingualtext.MonolingualText):
            lang = arg.language
            lang_code = lang.code
            return tfsl.monolingualtext.build_lemma(self.json["representations"][lang_code])
        raise KeyError(f"Can't get {type(arg)} from LexemeSense")

    def getitem_str(self, key: str) -> I.StatementList:
        """ :meta private: """
        if I.is_Pid(key):
            return self.getitem_pid(key)
        raise KeyError

    def getitem_pid(self, key: I.Pid) -> I.StatementList:
        """ :meta private: """
        return self.get_stmts(key)

    def get_stmts(self, prop: I.Pid) -> I.StatementList:
        """ Assembles a list of Statements present on the item with the given property. """
        return [tfsl.statement.build_statement(stmt) for stmt in self.json["claims"].get(prop,[])]
