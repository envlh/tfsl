import json
import os
import os.path
import time
from functools import singledispatchmethod
from textwrap import indent
from typing import Optional, List, Union

import tfsl.interfaces as I
import tfsl.auth
import tfsl.itemvalue
import tfsl.languages
import tfsl.lexemeform
import tfsl.lexemesense
import tfsl.monolingualtext
import tfsl.monolingualtextholder
import tfsl.statement
import tfsl.statementholder
import tfsl.utils

default_lexeme_cache_path = os.path.expanduser('~/.cache/tfsl')
os.makedirs(default_lexeme_cache_path,exist_ok=True)

class Lexeme:
    def __init__(self,
                lemmata: Union[tfsl.monolingualtextholder.MonolingualTextHolder, List[tfsl.monolingualtext.MonolingualText]],
                lang_in: tfsl.languages.Language,
                cat_in: I.Qid,
                statements: Optional[Union[
                    tfsl.statementholder.StatementHolder,
                    I.StatementSet,
                    List[tfsl.statement.Statement]
                 ]]=None,
                senses: Optional[List[tfsl.lexemesense.LexemeSense]]=None,
                forms: Optional[List[tfsl.lexemeform.LexemeForm]]=None):
        # TODO: better validation/type hinting and argument fallbacks
        super().__init__()
        if isinstance(lemmata, tfsl.monolingualtextholder.MonolingualTextHolder):
            self.lemmata = lemmata
        else:
            self.lemmata = tfsl.monolingualtextholder.MonolingualTextHolder(lemmata)
        
        if isinstance(statements, tfsl.statementholder.StatementHolder):
            self.statements = statements
        else:
            self.statements = tfsl.statementholder.StatementHolder(statements)

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
        self.lexeme_id: Optional[str] = None

    def get_published_settings(self) -> I.LexemePublishedSettings:
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

    def get_forms(self, inflections: Optional[List[I.Qid]]=None, exclusions: Optional[List[I.Qid]]=None) -> List[tfsl.lexemeform.LexemeForm]:
        if inflections is None:
            return self.forms
        initial_form_list = [form for form in self.forms
                if all(i in form.features for i in inflections)]
        if exclusions is None:
            return initial_form_list
        return [form for form in initial_form_list
                if all(i not in form.features for i in exclusions)]

    def get_senses(self) -> List[tfsl.lexemesense.LexemeSense]:
        return self.senses

    def get_language(self) -> tfsl.languages.Language:
        return self.language

    def __getitem__(self, key: object) -> Union[List[tfsl.statement.Statement], tfsl.lexemeform.LexemeForm, tfsl.lexemesense.LexemeSense, tfsl.monolingualtext.MonolingualText]:
        return self.getitem(key)

    @singledispatchmethod
    def getitem(self, key: object) -> Union[List[tfsl.statement.Statement], tfsl.lexemeform.LexemeForm, tfsl.lexemesense.LexemeSense, tfsl.monolingualtext.MonolingualText]:
        raise TypeError(f"Can't get {type(key)} from Lexeme")

    @getitem.register(tfsl.languages.Language)
    @getitem.register(tfsl.monolingualtext.MonolingualText)
    def _(self, key: tfsl.monolingualtextholder.lang_or_mt) -> tfsl.monolingualtext.MonolingualText:
        return self.lemmata[key]

    @getitem.register
    def _(self, key: str) -> Union[List[tfsl.statement.Statement], tfsl.lexemeform.LexemeForm, tfsl.lexemesense.LexemeSense]:
        def id_matches_key(obj: Union[tfsl.lexemeform.LexemeForm, tfsl.lexemesense.LexemeSense]) -> bool:
            return obj.id == key

        if I.is_Pid(key):
            return self.statements[key]
        if I.is_LFid(key):
            return next(filter(id_matches_key, self.forms))
        if I.is_LSid(key):
            return next(filter(id_matches_key, self.senses))

        if self.lexeme_id is not None:
            thing = self.lexeme_id
            def id_matches_key_suffix(obj: Union[tfsl.lexemeform.LexemeForm, tfsl.lexemesense.LexemeSense]) -> bool:
                return obj.id == '-'.join([thing, key])
            if I.is_Fid(key):
                return next(filter(id_matches_key_suffix, self.forms))
            if I.is_Sid(key):
                return next(filter(id_matches_key_suffix, self.senses))
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
    lemmas = tfsl.monolingualtextholder.build_text_list(lexeme_in["lemmas"])

    lexemecat = lexeme_in["lexicalCategory"]
    language = tfsl.languages.get_first_lang(lexeme_in["language"])

    statements = tfsl.statementholder.build_statement_list(lexeme_in["claims"])

    forms = [tfsl.lexemeform.build_form(form) for form in lexeme_in["forms"]]
    senses = [tfsl.lexemesense.build_sense(sense) for sense in lexeme_in["senses"]]

    lexeme_out = Lexeme(lemmas, language, lexemecat, statements, senses, forms)
    lexeme_out.set_published_settings(lexeme_in)
    return lexeme_out

# pylint: disable=invalid-name

def L(lid_in: Union[int, I.Lid, I.LFid, I.LSid]) -> Lexeme:
    lid: I.Lid
    if isinstance(lid_in, int):
        lid = I.Lid('L'+str(lid_in))
    elif I.is_LSid(lid_in):
        if split_lsid := I.split_LSid(lid_in):
            lid, _ = split_lsid
    elif I.is_LFid(lid_in):
        if split_lfid := I.split_LFid(lid_in):
            lid, _ = split_lfid
    elif I.is_Lid(lid_in):
        lid = lid_in
    filename = tfsl.utils.get_filename(lid)
    try:
        assert time.time() - os.path.getmtime(filename) < tfsl.utils.time_to_live
        with open(filename) as fileptr:
            lexeme_json = json.load(fileptr)
    except (FileNotFoundError, OSError, AssertionError):
        current_lexeme = tfsl.auth.get_lexemes([lid])
        lexeme_json = current_lexeme[lid]
        with open(filename, "w") as fileptr:
            json.dump(lexeme_json, fileptr)
    return build_lexeme(lexeme_json)
