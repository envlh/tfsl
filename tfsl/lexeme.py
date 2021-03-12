from collections import defaultdict
from copy import deepcopy
from functools import singledispatchmethod
from textwrap import indent

import tfsl.lexemeform
import tfsl.lexemesense
import tfsl.monolingualtext
import tfsl.statement
import tfsl.utils

class Lexeme:
    def __init__(self, lemmalist, lexemelang, lexemecat, statements=[], senses=[], forms=[]):
        # TODO: better validation/type hinting and argument fallbacks
        self.lemmata = [lemmalist] if type(lemmalist) != list else lemmalist
        self.language = lexemelang
        self.category = lexemecat
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
    
    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {type(arg)} to Lexeme")

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        return Lexeme(self.lemmata, self.language, self.category, tfsl.utils.add_claimlike(self.statements, arg), self.senses, self.forms)

    @add.register
    def _(self, arg: tfsl.lexemesense.LexemeSense):
        return Lexeme(self.lemmata, self.language, self.category, self.statements, tfsl.utils.add_to_list(self.senses, arg), self.forms)

    @add.register
    def _(self, arg: tfsl.lexemeform.LexemeForm):
        return Lexeme(self.lemmata, self.language, self.category, self.statements, self.senses, tfsl.utils.add_to_list(self.forms, arg))

    def __str__(self):
        # TODO: fix indentation of components
        lemma_strings = [str(lemma) for lemma in self.lemmata]
        lemma_str = '/'.join(lemma_strings)
        base_str = f': {self.category} in {self.language.item}'
        stmts_str = ""
        senses_str = ""
        forms_str = ""
        if(self.statements != {}):
            stmts_str = "\n<\n"+indent('\n'.join([str(stmt) for stmt in self.statements]), tfsl.utils.default_indent)+"\n>"
        if(len(self.senses) != 0):
            senses_str = "\n{\n"+indent('\n'.join([str(form) for form in self.forms]), tfsl.utils.default_indent)+"\n}"
        if(len(self.forms) != 0):
            forms_str = "\n(\n"+indent('\n'.join([str(sense) for sense in self.senses]), tfsl.utils.default_indent)+"\n)"
        return lemma_str + base_str + stmts_str + senses_str + forms_str

    def __jsonout__(self):
        base_dict = {"lexicalCategory": self.category, "language": self.language.item, "type": "lexeme"}
        base_dict["lemmas"] = {lemma.language.code: {"value": lemma.text, "language": lemma.language.code} for lemma in self.lemmata}
        base_dict["claims"] = self.statements
        if(base_dict["claims"] == {}):
            del base_dict["claims"]
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
