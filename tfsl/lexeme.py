""" Holds the Lexeme class and a function to build one given a JSON representation of it. """

import json
import os
import os.path
import time
from textwrap import indent
from typing import Collection, Optional, List, Protocol, Sequence, Union, overload

import tfsl.interfaces as I
import tfsl.auth
import tfsl.itemvalue
import tfsl.languages
import tfsl.lexemeform
import tfsl.lexemesense
import tfsl.monolingualtext
import tfsl.monolingualtextholder as MTH
import tfsl.statement
import tfsl.statementholder as STH
import tfsl.utils

class LexemeLike(I.MTST, Protocol):
    @property
    def lexeme_id(self) -> Optional[I.Lid]: ...
    @property
    def lemmata(self) -> MTH.MonolingualTextHolder:...
    @property
    def language(self) -> tfsl.languages.Language: ...
    @property
    def category(self) -> I.Qid: ...

    def get_forms(self, inflections: Optional[Collection[I.Qid]]=None, exclusions: Optional[Collection[I.Qid]]=None) -> Sequence[tfsl.lexemeform.LexemeFormLike]: ...

    def get_senses(self) -> Sequence[tfsl.lexemesense.LexemeSenseLike]: ...

    def repr_lemmata_first(self) -> str: ...

    @overload
    def __getitem__(self, arg: 'tfsl.languages.Language') -> 'tfsl.monolingualtext.MonolingualText': ...
    @overload
    def __getitem__(self, arg: 'tfsl.monolingualtext.MonolingualText') -> 'tfsl.monolingualtext.MonolingualText': ...
    @overload
    def __getitem__(self, arg: I.Pid) -> I.StatementList: ...
    @overload
    def __getitem__(self, arg: 'tfsl.itemvalue.ItemValue') -> I.StatementList: ...
    @overload
    def __getitem__(self, key: I.LFid) -> tfsl.lexemeform.LexemeFormLike: ...
    @overload
    def __getitem__(self, key: I.LSid) -> tfsl.lexemesense.LexemeSenseLike: ...
    @overload
    def __getitem__(self, key: I.Fid) -> tfsl.lexemeform.LexemeFormLike: ...
    @overload
    def __getitem__(self, key: I.Sid) -> tfsl.lexemesense.LexemeSenseLike: ...

class Lexeme:
    """ Container for a Wikidata lexeme. """
    def __init__(self,
                lemmata: Union[MTH.MonolingualTextHolder, I.MonolingualTextHolderInput],
                lang_in: tfsl.languages.Language,
                cat_in: I.Qid,
                statements: Optional[Union[STH.StatementHolder, I.StatementHolderInput]]=None,
                senses: Optional[I.LexemeSenseList]=None,
                forms: Optional[I.LexemeFormList]=None):
        super().__init__()
        if isinstance(lemmata, MTH.MonolingualTextHolder):
            self.lemmata = lemmata
        else:
            self.lemmata = MTH.MonolingualTextHolder(lemmata)

        if isinstance(statements, STH.StatementHolder):
            self.statements = statements
        else:
            self.statements = STH.StatementHolder(statements)

        self.language = lang_in
        self.category = cat_in

        if senses is None:
            self.senses = []
        else:
            self.senses = senses

        if forms is None:
            self.forms = []
        else:
            self.forms = forms

        self.pageid: Optional[int] = None
        self.namespace: Optional[int] = None
        self.title: Optional[str] = None
        self.lastrevid: Optional[int] = None
        self.modified: Optional[str] = None
        self.lexeme_type: Optional[str] = None
        self.lexeme_id: Optional[I.Lid] = None

    def get_published_settings(self) -> I.LexemePublishedSettings:
        """ Returns a dictionary containing those portions of the Lexeme JSON dictionary
            which are only significant at editing time for existing lexemes.
        """
        if self.pageid is not None and self.namespace is not None and self.title is not None and self.lastrevid is not None and self.modified is not None and self.lexeme_type is not None and self.lexeme_id is not None:
            return {
                "pageid": self.pageid,
                "ns": self.namespace,
                "title": self.title,
                "lastrevid": self.lastrevid,
                "modified": self.modified,
                "type": self.lexeme_type,
                "id": self.lexeme_id
            }
        return {}

    def set_published_settings(self, lexeme_in: I.LexemePublishedSettings) -> None:
        """ Sets based on a Lexeme JSON dictionary those variables
            which are only significant at editing time for existing lexemes.
        """
        if "pageid" in lexeme_in:
            self.pageid = lexeme_in["pageid"]
            self.namespace = lexeme_in["ns"]
            self.title = lexeme_in["title"]
            self.lastrevid = lexeme_in["lastrevid"]
            self.modified = lexeme_in["modified"]
            self.lexeme_type = lexeme_in["type"]
            self.lexeme_id = lexeme_in["id"]

    def __add__(self, arg: object) -> 'Lexeme':
        if isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                        self.statements + arg,
                        self.senses, self.forms)
            lexeme_out.set_published_settings(published_settings)
            return lexeme_out
        elif isinstance(arg, tfsl.lexemesense.LexemeSense):
            published_settings = self.get_published_settings()
            lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                        self.statements, tfsl.utils.add_to_list(self.senses, arg),
                        self.forms)
            lexeme_out.set_published_settings(published_settings)
            return lexeme_out
        elif isinstance(arg, tfsl.lexemeform.LexemeForm):
            published_settings = self.get_published_settings()
            lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                        self.statements, self.senses,
                        tfsl.utils.add_to_list(self.forms, arg))
            lexeme_out.set_published_settings(published_settings)
            return lexeme_out
        elif isinstance(arg, tfsl.monolingualtext.MonolingualText):
            published_settings = self.get_published_settings()
            lexeme_out = Lexeme(self.lemmata + arg,
                        self.language, self.category, self.statements,
                        self.senses, self.forms)
            lexeme_out.set_published_settings(published_settings)
            return lexeme_out
        raise NotImplementedError(f"Can't add {type(arg)} to Lexeme")

    def __sub__(self, arg: object) -> 'Lexeme':
        if isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                        self.statements - arg,
                        self.senses, self.forms)
            lexeme_out.set_published_settings(published_settings)
            return lexeme_out
        elif isinstance(arg, tfsl.lexemesense.LexemeSense):
            published_settings = self.get_published_settings()
            lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                        self.statements,
                        tfsl.utils.sub_from_list(self.senses, arg),
                        self.forms)
            lexeme_out.set_published_settings(published_settings)
            return lexeme_out
        elif isinstance(arg, tfsl.lexemeform.LexemeForm):
            published_settings = self.get_published_settings()
            lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                        self.statements, self.senses,
                        tfsl.utils.sub_from_list(self.forms, arg))
            lexeme_out.set_published_settings(published_settings)
            return lexeme_out
        elif isinstance(arg, tfsl.monolingualtext.MonolingualText):
            published_settings = self.get_published_settings()
            lexeme_out = Lexeme(self.lemmata - arg,
                        self.language, self.category, self.statements,
                        self.senses, self.forms)
            lexeme_out.set_published_settings(published_settings)
            return lexeme_out
        raise NotImplementedError(f"Can't subtract {type(arg)} from Lexeme")

    def get_forms(self, inflections: Optional[Collection[I.Qid]]=None, exclusions: Optional[Collection[I.Qid]]=None) -> I.LexemeFormList:
        """ Returns those forms on the lexeme with the provided inflectional features,
            excluding those listed in the exclusions list.
        """
        if inflections is None:
            return self.forms
        initial_form_list = [form for form in self.forms
                if all(i in form.features for i in inflections)]
        if exclusions is None:
            return initial_form_list
        return [form for form in initial_form_list
                if all(i not in form.features for i in exclusions)]

    def get_senses(self) -> I.LexemeSenseList:
        """ Returns the list of senses on the lexeme. """
        return self.senses

    def get_language(self) -> tfsl.languages.Language:
        """ Returns the language of the lexeme. """
        return self.language

    @overload
    def __getitem__(self, key: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText: ...
    @overload
    def __getitem__(self, key: tfsl.monolingualtext.MonolingualText) -> tfsl.monolingualtext.MonolingualText: ...
    @overload
    def __getitem__(self, key: I.Pid) -> I.StatementList: ...
    @overload
    def __getitem__(self, arg: 'tfsl.itemvalue.ItemValue') -> I.StatementList: ...
    @overload
    def __getitem__(self, key: I.LFid) -> tfsl.lexemeform.LexemeForm: ...
    @overload
    def __getitem__(self, key: I.LSid) -> tfsl.lexemesense.LexemeSense: ...
    @overload
    def __getitem__(self, key: I.Fid) -> tfsl.lexemeform.LexemeForm: ...
    @overload
    def __getitem__(self, key: I.Sid) -> tfsl.lexemesense.LexemeSense: ...

    def __getitem__(self, key: object) -> Union[I.StatementList, tfsl.lexemeform.LexemeForm, tfsl.lexemesense.LexemeSense, tfsl.monolingualtext.MonolingualText]:
        if isinstance(key, tfsl.languages.Language) or isinstance(key, tfsl.monolingualtext.MonolingualText):
            return self.lemmata[key]
        elif isinstance(key, str):
            return self.getitem_str(key)
        elif isinstance(key, tfsl.itemvalue.ItemValue):
            return self.getitem_str(key.id)
        raise TypeError(f"Can't get {type(key)} from Lexeme")

    def getitem_pid(self, key: I.Pid) -> I.StatementList:
        return self.statements[key]

    def getitem_fid(self, key: I.LFid) -> tfsl.lexemeform.LexemeForm:
        for form in self.forms:
            if form.id == key:
                return form
        raise KeyError

    def getitem_sid(self, key: I.LSid) -> tfsl.lexemesense.LexemeSense:
        for sense in self.senses:
            if sense.id == key:
                return sense
        raise KeyError

    def getitem_str(self, key: str) -> Union[I.StatementList, tfsl.lexemeform.LexemeForm, tfsl.lexemesense.LexemeSense]:
        """ Common handling of __getitem__ for inputs as strings or the ids of ItemValues. """
        if I.is_Pid(key):
            return self.getitem_pid(key)
        elif I.is_LFid(key):
            return self.getitem_fid(key)
        elif I.is_LSid(key):
            return self.getitem_sid(key)
        elif self.lexeme_id is not None:
            new_key = '-'.join([self.lexeme_id, key])
            if I.is_LFid(new_key):
                return self.getitem_fid(new_key)
            elif I.is_LSid(new_key):
                return self.getitem_sid(new_key)
        raise KeyError

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return self.statements.haswbstatement(property_in, value_in)

    def __str__(self) -> str:
        # TODO: fix indentation of components
        lemma_str = str(self.lemmata)
        base_str = f': {self.category} in {self.language.item}'

        stmts_str = str(self.statements)

        senses_str = ""
        if len(self.senses) != 0:
            prefix = "{\n"
            suffix = "\n}"
            sense_strings = [str(sense) for sense in self.senses]
            base_str = indent('\n'.join(sense_strings), tfsl.utils.DEFAULT_INDENT)
            senses_str = prefix + base_str + suffix

        forms_str = ""
        if len(self.forms) != 0:
            prefix = "(\n"
            suffix = "\n)"
            form_strings = [str(form) for form in self.forms]
            base_str = indent('\n'.join(form_strings), tfsl.utils.DEFAULT_INDENT)
            forms_str = prefix + base_str + suffix

        return "\n".join([lemma_str + base_str, stmts_str, senses_str, forms_str])

    def __repr__(self) -> str:
        return self.lexeme_id or "L0" + f" ({self.language.item}): " + str(self.lemmata)

    def repr_lemmata_first(self) -> str:
        return str(self.lemmata) + ": " + (self.lexeme_id or "L0") + f" ({self.language.item})"

    def __jsonout__(self) -> I.LexemeDict:
        lemma_dict: I.LemmaDictSet = self.lemmata.__jsonout__()

        statement_dict: I.StatementDictSet = self.statements.__jsonout__()

        form_list: List[I.LexemeFormDict] = [form.__jsonout__() for form in self.forms]

        sense_list: List[I.LexemeSenseDict] = [sense.__jsonout__() for sense in self.senses]

        base_dict: I.LexemeDict = {
            "lexicalCategory": self.category,
            "language": self.language.item,
            "type": "lexeme",
            "lemmas": lemma_dict,
            "claims": statement_dict,
            "forms": form_list,
            "senses": sense_list
        }

        if self.lexeme_id is not None and self.lastrevid is not None:
            base_dict["id"] = self.lexeme_id
            base_dict["lastrevid"] = self.lastrevid

        return base_dict


def build_lexeme(lexeme_in: I.LexemeDict) -> Lexeme:
    """ Builds a Lexeme from the JSON dictionary describing it. """
    lemmas = MTH.build_text_list(lexeme_in["lemmas"])

    lexemecat = lexeme_in["lexicalCategory"]
    language = tfsl.languages.get_first_lang(lexeme_in["language"])

    statements = STH.build_statement_list(lexeme_in["claims"])

    forms = [tfsl.lexemeform.build_form(form) for form in lexeme_in["forms"]]
    senses = [tfsl.lexemesense.build_sense(sense) for sense in lexeme_in["senses"]]

    lexeme_out = Lexeme(lemmas, language, lexemecat, statements, senses, forms)
    lexeme_out.set_published_settings(lexeme_in)
    return lexeme_out

def retrieve_lexeme_json(lid_in: Union[int, I.Lid, I.LFid, I.LSid, tfsl.itemvalue.ItemValue]) -> I.LexemeDict:
    lid: I.Lid
    if isinstance(lid_in, int):
        lid = I.Lid('L'+str(lid_in))
    elif isinstance(lid_in, tfsl.itemvalue.ItemValue):
        if lid_in.type == "lexeme" and I.is_Lid(lid_in.id):
            lid = lid_in.id
        if lid_in.type == "form" and I.is_LFid(lid_in.id):
            if split_lfid := I.split_LFid(lid_in.id):
                lid, _ = split_lfid
        if lid_in.type == "sense" and I.is_LSid(lid_in.id):
            if split_lsid := I.split_LSid(lid_in.id):
                lid, _ = split_lsid
    elif I.is_LSid(lid_in):
        if split_lsid := I.split_LSid(lid_in):
            lid, _ = split_lsid
    elif I.is_LFid(lid_in):
        if split_lfid := I.split_LFid(lid_in):
            lid, _ = split_lfid
    elif I.is_Lid(lid_in):
        lid = lid_in
    filename = tfsl.utils.get_filename(lid)
    lexeme_json: I.LexemeDict
    try:
        assert time.time() - os.path.getmtime(filename) < tfsl.utils.time_to_live
        with open(filename, encoding="utf-8") as fileptr:
            lexeme_json = json.load(fileptr)
    except (FileNotFoundError, OSError, AssertionError) as e:
        current_lexeme = tfsl.auth.get_lexemes([lid])
        current_lid_output = current_lexeme[lid]
        if I.is_LexemeDict(current_lid_output):
            lexeme_json = current_lid_output
        else:
            raise ValueError(f"Retrieved entity {lid} was not an item") from e
        with open(filename, "w", encoding="utf-8") as fileptr:
            json.dump(lexeme_json, fileptr)
    return lexeme_json

def L(lid_in: Union[int, I.Lid, I.LFid, I.LSid, tfsl.itemvalue.ItemValue]) -> Lexeme:
    """ Retrieves and returns the lexeme with the provided Lid. """
    lexeme_json = retrieve_lexeme_json(lid_in)
    return build_lexeme(lexeme_json)

# pylint: disable=invalid-name

class L_:
    """ A Lexeme, but lemmata/form representations are not auto-converted to MonolingualTexts,
        statements are only assembled into Statements when accessed,
        and forms and senses are returned as LF_ and LS_ objects instead of LexemeForms and LexemeSenses.
    """
    def __init__(self, input_arg: Union[int, I.Lid, I.LFid, I.LSid, tfsl.itemvalue.ItemValue]):
        self.lexeme_json: I.LexemeDict = retrieve_lexeme_json(input_arg)

    @property
    def lemmata(self) -> MTH.MonolingualTextHolder:
        return MTH.MonolingualTextHolder(MTH.build_text_list(self.lexeme_json["lemmas"]))

    @property
    def category(self) -> I.Qid:
        return self.lexeme_json["lexicalCategory"]

    @property
    def language(self) -> tfsl.languages.Language:
        return self.get_language()

    @property
    def lexeme_id(self) -> I.Lid:
        return self.lexeme_json["id"]

    def __repr__(self) -> str:
        return self.lexeme_json['id'] + f" ({self.lexeme_json['language']}): " + " / ".join(f"{x['value']}@{x['language']}" for _, x in self.lexeme_json["lemmas"].items())

    def repr_lemmata_first(self) -> str:
        return " / ".join(f"{x['value']}@{x['language']}" for _, x in self.lexeme_json["lemmas"].items()) + ": " + self.lexeme_json['id'] + f" ({self.lexeme_json['language']})"

    def get_stmts(self, prop: I.Pid) -> I.StatementList:
        """ Assembles a list of Statements present on the item with the given property. """
        return [tfsl.statement.build_statement(stmt) for stmt in self.lexeme_json["claims"].get(prop,[])]

    def get_forms(self, inflections: Optional[Collection[I.Qid]]=None, exclusions: Optional[Collection[I.Qid]]=None) -> List[tfsl.lexemeform.LF_]:
        if inflections is None:
            return [tfsl.lexemeform.LF_(form) for form in self.lexeme_json["forms"]]
        initial_form_list = [tfsl.lexemeform.LF_(form) for form in self.lexeme_json["forms"]
                if all(i in form["grammaticalFeatures"] for i in inflections)]
        if exclusions is None:
            return initial_form_list
        return [form for form in initial_form_list
                if all(i not in form.features for i in exclusions)]

    def get_senses(self) -> List[tfsl.lexemesense.LS_]:
        return [tfsl.lexemesense.LS_(sense) for sense in self.lexeme_json["senses"]]

    def get_language(self) -> tfsl.languages.Language:
        return tfsl.languages.get_first_lang(self.lexeme_json["language"])

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        return STH.haswbstatement(self.lexeme_json["claims"], property_in, value_in)

    @overload
    def __getitem__(self, key: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText: ...
    @overload
    def __getitem__(self, key: tfsl.monolingualtext.MonolingualText) -> tfsl.monolingualtext.MonolingualText: ...
    @overload
    def __getitem__(self, key: I.Pid) -> I.StatementList: ...
    @overload
    def __getitem__(self, arg: 'tfsl.itemvalue.ItemValue') -> I.StatementList: ...
    @overload
    def __getitem__(self, key: I.LFid) -> tfsl.lexemeform.LF_: ...
    @overload
    def __getitem__(self, key: I.LSid) -> tfsl.lexemesense.LS_: ...
    @overload
    def __getitem__(self, key: I.Fid) -> tfsl.lexemeform.LF_: ...
    @overload
    def __getitem__(self, key: I.Sid) -> tfsl.lexemesense.LS_: ...

    def __getitem__(self, key: object) -> Union[I.StatementList, tfsl.lexemeform.LF_, tfsl.lexemesense.LS_, tfsl.monolingualtext.MonolingualText]:
        if isinstance(key, tfsl.languages.Language):
            return MTH.get_lang_from_mtlist(self.lexeme_json["lemmas"], key)
        elif isinstance(key, tfsl.monolingualtext.MonolingualText):
            lang = key.language
            lang_code = lang.code
            return tfsl.monolingualtext.build_lemma(self.lexeme_json["lemmas"][lang_code])
        elif isinstance(key, str):
            return self.getitem_str(key)
        elif isinstance(key, tfsl.itemvalue.ItemValue):
            return self.getitem_str(key.id)
        raise TypeError(f"Can't get {type(key)} from Lexeme")

    def getitem_pid(self, key: I.Pid) -> I.StatementList:
        return self.get_stmts(key)

    def getitem_fid(self, key: I.LFid) -> tfsl.lexemeform.LF_:
        for form in self.lexeme_json["forms"]:
            if form["id"] == key:
                return tfsl.lexemeform.LF_(form)
        raise KeyError

    def getitem_sid(self, key: I.LSid) -> tfsl.lexemesense.LS_:
        for sense in self.lexeme_json["senses"]:
            if sense["id"] == key:
                return tfsl.lexemesense.LS_(sense)
        raise KeyError

    def getitem_str(self, key: str) -> Union[I.StatementList, tfsl.lexemeform.LF_, tfsl.lexemesense.LS_]:
        """ Common handling of __getitem__ for inputs as strings or the ids of ItemValues. """
        if I.is_Pid(key):
            return self.getitem_pid(key)
        elif I.is_LFid(key):
            return self.getitem_fid(key)
        elif I.is_LSid(key):
            return self.getitem_sid(key)
        elif self.lexeme_json["id"] is not None:
            lexeme_id = self.lexeme_json["id"]
            new_key = '-'.join([lexeme_id, key])
            if I.is_LFid(new_key):
                return self.getitem_fid(new_key)
            elif I.is_LSid(new_key):
                return self.getitem_sid(new_key)
        raise KeyError
