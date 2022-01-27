from collections import defaultdict
from functools import singledispatchmethod
from textwrap import indent

import tfsl.monolingualtext
import tfsl.monolingualtextholder
import tfsl.statement
import tfsl.statementholder
import tfsl.utils

class LexemeSense(
    tfsl.statementholder.StatementHolder,
    tfsl.monolingualtextholder.MonolingualTextHolder
):
    def __init__(self, glosses=None, statements=None):
        super().__init__(texts=glosses, statements=statements)

        self.glosses = self.texts

        self.id = None

    def __getitem__(self, key):
        if tfsl.utils.matches_property(key):
            return self.statements.get(key, [])
        raise KeyError

    def __add__(self, arg):
        return self.add(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {type(arg)} to LexemeSense")

    @add.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return LexemeSense(tfsl.utils.add_to_mtlist(self.glosses, arg), self.statements)

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        return LexemeSense(self.glosses, tfsl.utils.add_claimlike(self.statements, arg))

    def __sub__(self, arg):
        return self.sub(arg)

    @singledispatchmethod
    def sub(self, arg):
        raise NotImplementedError(f"Can't subtract {type(arg)} from LexemeForm")

    @sub.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return LexemeSense(tfsl.utils.sub_from_list(self.glosses, arg), self.statements)

    @sub.register
    def _(self, arg: tfsl.languages.Language):
        return LexemeSense(tfsl.utils.remove_replang(self.glosses, arg), self.statements)

    @sub.register
    def _(self, arg: str):
        if tfsl.utils.matches_property(arg):
            return LexemeSense(self.glosses, tfsl.utils.sub_property(self.statements, arg))

    @sub.register
    def _(self, arg: tfsl.statement.Statement):
        return LexemeSense(self.glosses, tfsl.utils.sub_claimlike(self.statements, arg))

    def __contains__(self, arg):
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg):
        return arg in self.statements[arg.property]

    @contains.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return arg in self.glosses

    @contains.register
    def _(self, arg: str):
        if tfsl.utils.matches_property(arg):
            return arg in self.statements

    @contains.register
    def _(self, arg: tfsl.claim.Claim):
        return any((arg in self.statements[prop]) for prop in self.statements)

    @contains.register
    def _(self, arg: tfsl.languages.Language):
        return any((gloss.language == arg) for gloss in self.glosses)

    def __eq__(self, rhs):
        glosses_equal = tfsl.monolingualtextholder.MonolingualTextHolder.__eq__(self, rhs)
        statements_equal = tfsl.statementholder.StatementHolder.__eq__(self, rhs)
        return glosses_equal and statements_equal

    def __str__(self):
        # TODO: output everything else
        base_str = ' / '.join([str(gloss) for gloss in self.glosses])
        stmt_str = ""
        if self.statements != {}:
            stmt_str = "\n<\n"+indent("\n".join([str(stmt) for prop in self.statements for stmt in self.statements[prop]]), tfsl.utils.DEFAULT_INDENT)+"\n>"
        return base_str + stmt_str

    def __jsonout__(self):
        glosses_dict = self.build_text_dict()
        base_dict = {"glosses": glosses_dict}

        if self.id is not None:
            base_dict["id"] = self.id
        else:
            base_dict["add"] = ""

        if (statement_dict := self.build_statement_dict()):
            base_dict["claims"] = statement_dict

        return base_dict

def build_sense(sense_in):
    glosses = tfsl.monolingualtextholder.build_text_list(sense_in["glosses"])

    statements = tfsl.statementholder.build_statement_list(sense_in["claims"])

    sense_out = LexemeSense(glosses, statements)
    sense_out.id = sense_in["id"]
    return sense_out
