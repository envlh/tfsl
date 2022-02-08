import json
import os
import os.path
import time
from functools import singledispatchmethod
from textwrap import indent

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
    def __init__(self, lemmata, lang_in, cat_in,
                 statements=None, senses=None, forms=None):
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
            self.senses = senses if isinstance(senses, list) else [senses]

        if forms is None:
            self.forms = []
        else:
            self.forms = forms if isinstance(forms, list) else [forms]

        self.pageid = None
        self.namespace = None
        self.title = None
        self.lastrevid = None
        self.modified = None
        self.lexeme_type = None
        self.lexeme_id = None

    def get_published_settings(self):
        return {
            "pageid": self.pageid,
            "ns": self.namespace,
            "title": self.title,
            "lastrevid": self.lastrevid,
            "modified": self.modified,
            "type": self.lexeme_type,
            "id": self.lexeme_id
        }

    def set_published_settings(self, lexeme_in):
        self.pageid = lexeme_in["pageid"]
        self.namespace = lexeme_in["ns"]
        self.title = lexeme_in["title"]
        self.lastrevid = lexeme_in["lastrevid"]
        self.modified = lexeme_in["modified"]
        self.lexeme_type = lexeme_in["type"]
        self.lexeme_id = lexeme_in["id"]

    def __add__(self, arg):
        return self.add(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {type(arg)} to Lexeme")

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        published_settings = self.get_published_settings()
        lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                      self.statements + arg,
                      self.senses, self.forms)
        lexeme_out.set_published_settings(published_settings)
        return lexeme_out

    @add.register
    def _(self, arg: tfsl.lexemesense.LexemeSense):
        published_settings = self.get_published_settings()
        lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                      self.statements, tfsl.utils.add_to_list(self.senses, arg),
                      self.forms)
        lexeme_out.set_published_settings(published_settings)
        return lexeme_out

    @add.register
    def _(self, arg: tfsl.lexemeform.LexemeForm):
        published_settings = self.get_published_settings()
        lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                      self.statements, self.senses,
                      tfsl.utils.add_to_list(self.forms, arg))
        lexeme_out.set_published_settings(published_settings)
        return lexeme_out

    @add.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        published_settings = self.get_published_settings()
        lexeme_out = Lexeme(self.lemmata + arg,
                      self.language, self.category, self.statements,
                      self.senses, self.forms)
        lexeme_out.set_published_settings(published_settings)
        return lexeme_out

    def __sub__(self, arg):
        return self.sub(arg)

    @singledispatchmethod
    def sub(self, arg):
        raise NotImplementedError(f"Can't subtract {type(arg)} from Lexeme")

    @sub.register
    def _(self, arg: tfsl.statement.Statement):
        published_settings = self.get_published_settings()
        lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                      self.statements - arg,
                      self.senses, self.forms)
        lexeme_out.set_published_settings(published_settings)
        return lexeme_out

    @sub.register
    def _(self, arg: tfsl.lexemesense.LexemeSense):
        published_settings = self.get_published_settings()
        lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                      self.statements,
                      tfsl.utils.sub_from_list(self.senses, arg),
                      self.forms)
        lexeme_out.set_published_settings(published_settings)
        return lexeme_out

    @sub.register
    def _(self, arg: tfsl.lexemeform.LexemeForm):
        published_settings = self.get_published_settings()
        lexeme_out = Lexeme(self.lemmata, self.language, self.category,
                      self.statements, self.senses,
                      tfsl.utils.sub_from_list(self.forms, arg))
        lexeme_out.set_published_settings(published_settings)
        return lexeme_out

    @sub.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        published_settings = self.get_published_settings()
        lexeme_out = Lexeme(self.lemmata - arg,
                      self.language, self.category, self.statements,
                      self.senses, self.forms)
        lexeme_out.set_published_settings(published_settings)
        return lexeme_out

    def get_forms(self, inflections=None, exclusions=None):
        if inflections is None:
            return self.forms
        initial_form_list = [form for form in self.forms
                if all(i in form.features for i in inflections)]
        if exclusions is None:
            return initial_form_list
        return [form for form in initial_form_list
                if all(i not in form.features for i in exclusions)]

    def get_senses(self, specifiers=None):
        # TODO: handle specifiers argument
        if specifiers is None:
            return self.senses

    def get_language(self):
        return self.language

    def __getitem__(self, key):
        return self.getitem(key)

    @singledispatchmethod
    def getitem(self, key):
        raise TypeError(f"Can't get {type(key)} from Lexeme")

    @getitem.register(tfsl.languages.Language)
    @getitem.register(tfsl.monolingualtext.MonolingualText)
    def _(self, key: tfsl.monolingualtextholder.lang_or_mt):
        return self.lemmata[key]

    @getitem.register
    def _(self, key: str):
        id_matches_key = lambda obj: obj.id == key
        id_matches_key_suffix = lambda obj: obj.id == '-'.join([self.lexeme_id, key])

        if tfsl.utils.matches_property(key):
            return self.statements[key]
        if tfsl.utils.matches_form(key):
            return next(filter(id_matches_key, self.forms))
        if tfsl.utils.matches_form_suffix(key):
            return next(filter(id_matches_key_suffix, self.forms))
        if tfsl.utils.matches_sense(key):
            return next(filter(id_matches_key, self.senses))
        if tfsl.utils.matches_sense_suffix(key):
            return next(filter(id_matches_key_suffix, self.senses))
        raise KeyError

    def haswbstatement(self, property_in, value_in=None):
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return self.statements.haswbstatement(property_in, value_in)

    def __str__(self):
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

    def __jsonout__(self):
        base_dict = {"lexicalCategory": self.category,
                     "language": self.language.item,
                     "type": "lexeme"}

        base_dict["lemmas"] = self.lemmata.__jsonout__()

        if (statement_dict := self.statements.__jsonout__()):
            base_dict["claims"] = statement_dict

        if (form_list := [form.__jsonout__() for form in self.forms]):
            base_dict["forms"] = form_list

        if (sense_list := [sense.__jsonout__() for sense in self.senses]):
            base_dict["senses"] = sense_list

        if self.lexeme_id is not None:
            base_dict["id"] = self.lexeme_id
            base_dict["lastrevid"] = self.lastrevid

        return base_dict


def build_lexeme(lexeme_in):
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

def L(lid):
    if isinstance(lid, int):
        lid = 'L'+str(lid)
    elif match := tfsl.utils.matches_sense(lid):
        lid = match.group(1)
    elif match := tfsl.utils.matches_form(lid):
        lid = match.group(1)
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
