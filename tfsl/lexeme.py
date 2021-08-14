from collections import defaultdict
from copy import deepcopy
from functools import singledispatchmethod
from textwrap import indent

import tfsl.auth
import tfsl.languages
import tfsl.lexemeform
import tfsl.lexemesense
import tfsl.monolingualtext
import tfsl.statement
import tfsl.utils


class Lexeme:
    def __init__(self, lemmalist, lang_in, cat_in,
                 statements=[], senses=[], forms=[]):
        # TODO: better validation/type hinting and argument fallbacks
        self.lemmata = [lemmalist] if type(lemmalist) != list else lemmalist
        self.language = lang_in
        self.category = cat_in
        if(type(statements) == list):
            self.statements = defaultdict(list)
            for arg in statements:
                self.statements[arg.property].append(arg)
        else:
            self.statements = deepcopy(statements)
        self.senses = [senses] if type(senses) != list else senses
        self.forms = [forms] if type(forms) != list else forms

    def __add__(self, arg):
        return self.add(arg)

    def __sub__(self, arg):
        return self.sub(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {type(arg)} to Lexeme")

    @singledispatchmethod
    def sub(self, arg):
        raise NotImplementedError(f"Can't subtract {type(arg)} from Lexeme")

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        return Lexeme(self.lemmata, self.language, self.category,
                      tfsl.utils.add_claimlike(self.statements, arg),
                      self.senses, self.forms)

    @sub.register
    def _(self, arg: tfsl.statement.Statement):
        return Lexeme(self.lemmata, self.language, self.category,
                      tfsl.utils.sub_claimlike(self.statements, arg),
                      self.senses, self.forms)

    @add.register
    def _(self, arg: tfsl.lexemesense.LexemeSense):
        return Lexeme(self.lemmata, self.language, self.category,
                      self.statements, tfsl.utils.add_to_list(self.senses, arg),
                      self.forms)

    @sub.register
    def _(self, arg: tfsl.lexemesense.LexemeSense):
        return Lexeme(self.lemmata, self.language, self.category,
                      self.statements,
                      tfsl.utils.sub_from_list(self.senses, arg),
                      self.forms)

    @add.register
    def _(self, arg: tfsl.lexemeform.LexemeForm):
        return Lexeme(self.lemmata, self.language, self.category,
                      self.statements, self.senses,
                      tfsl.utils.add_to_list(self.forms, arg))

    @sub.register
    def _(self, arg: tfsl.lexemeform.LexemeForm):
        return Lexeme(self.lemmata, self.language, self.category,
                      self.statements, self.senses,
                      tfsl.utils.sub_from_list(self.forms, arg))

    @add.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return Lexeme(tfsl.utils.add_to_mtlist(self.lemmata, arg),
                      self.language, self.category, self.statements,
                      self.senses, self.forms)

    @sub.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return Lexeme(tfsl.utils.sub_from_list(self.lemmata, arg),
                      self.language, self.category, self.statements,
                      self.senses, self.forms)

    def getForms(self, inflections=[]):
        if len(inflections) == 0:
            return self.forms
        return [form for form in self.forms
                if all(i in form.features for i in inflections)]

    def getSenses(self, specifiers=None):
        # TODO: handle specifiers argument
        if specifiers is None:
            return self.senses

    def getLanguage(self):
        return self.language

    def __str__(self):
        # TODO: fix indentation of components
        lemma_strings = [str(lemma) for lemma in self.lemmata]
        lemma_str = '/'.join(lemma_strings)
        base_str = f': {self.category} in {self.language.item}'

        stmts_str = ""
        if(self.statements != {}):
            prefix = "\n<\n"
            suffix = "\n>"
            stmt_strings = [str(stmt) for stmt in self.statements]
            base_str = indent('\n'.join(stmt_strings), tfsl.utils.default_indent)
            stmts_str = prefix + base_str + suffix

        senses_str = ""
        if(len(self.senses) != 0):
            prefix = "\n{\n"
            suffix = "\n}"
            sense_strings = [str(sense) for sense in self.senses]
            base_str = indent('\n'.join(sense_strings), tfsl.utils.default_indent)
            senses_str = prefix + base_str + suffix

        forms_str = ""
        if(len(self.forms) != 0):
            prefix = "\n(\n"
            suffix = "\n)"
            form_strings = [str(form) for form in self.forms]
            base_str = indent('\n'.join(form_strings), tfsl.utils.default_indent)
            forms_str = prefix + base_str + suffix

        return lemma_str + base_str + stmts_str + senses_str + forms_str

    def __jsonout__(self):
        base_dict = {"lexicalCategory": self.category,
                     "language": self.language.item,
                     "type": "lexeme"}

        base_dict["lemmas"] = {}
        for lemma in self.lemmata:
            new_dict = {"value": lemma.text, "language": lemma.language.code}
            base_dict["lemmas"][lemma.language.code] = new_dict

        base_dict["claims"] = defaultdict(list)
        for stmtprop in self.statements:
            for stmtval in self.statements[stmtprop]:
                base_dict["claims"][stmtprop].append(stmtval.__jsonout__())
        if(base_dict["claims"] == {}):
            del base_dict["claims"]
        else:
            base_dict["claims"] = dict(base_dict["claims"])

        base_dict["forms"] = [form.__jsonout__() for form in self.forms]
        if(base_dict["forms"] == []):
            del base_dict["forms"]

        base_dict["senses"] = [sense.__jsonout__() for sense in self.senses]
        if(base_dict["senses"] == []):
            del base_dict["senses"]

        try:
            base_dict["id"] = self.id
            base_dict["lastrevid"] = self.lastrevid
        except AttributeError:
            pass

        return base_dict


def build_lexeme(lexeme_in):
    lemmas = []
    for code, lemma in lexeme_in["lemmas"].items():
        new_lemma = lemma["value"] @ tfsl.languages.get_first_lang(lemma["language"])
        lemmas.append(new_lemma)

    lexemecat = lexeme_in["lexicalCategory"]
    language = tfsl.languages.get_first_lang(lexeme_in["language"])

    statements_in = lexeme_in["claims"]
    statements = defaultdict(list)
    for prop in statements_in:
        for claim in statements_in[prop]:
            statements[prop].append(tfsl.statement.build_statement(claim))

    forms = [tfsl.lexemeform.build_form(form) for form in lexeme_in["forms"]]
    senses = [tfsl.lexemesense.build_sense(sense) for sense in lexeme_in["senses"]]

    lexeme_out = Lexeme(lemmas, language, lexemecat, statements, senses, forms)
    lexeme_out.pageid = lexeme_in["pageid"]
    lexeme_out.ns = lexeme_in["ns"]
    lexeme_out.title = lexeme_in["title"]
    lexeme_out.lastrevid = lexeme_in["lastrevid"]
    lexeme_out.modified = lexeme_in["modified"]
    lexeme_out.lexeme_type = lexeme_in["type"]
    lexeme_out.id = lexeme_in["id"]
    return lexeme_out
