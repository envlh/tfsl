from functools import singledispatchmethod
from typing import Union

import tfsl.monolingualtext
import tfsl.monolingualtextholder
import tfsl.statement
import tfsl.statementholder
import tfsl.utils

class LexemeSense(
    tfsl.monolingualtextholder.MonolingualTextHolder,
    tfsl.statementholder.StatementHolder
):
    def __init__(self, glosses, statements=None):
        super().__init__(texts=glosses, statements=statements)

        self.glosses = self.texts
        self.removed_glosses = self.removed_texts
        self.id = None

    def __getitem__(self, arg):
        return self.getitem(arg)

    @singledispatchmethod
    def getitem(self, arg):
        raise KeyError(f"Can't get {type(arg)} from LexemeSense")

    @getitem.register
    def _(self, arg: str):
        return tfsl.statementholder.StatementHolder.__getitem__(self, arg)

    @getitem.register
    def _(self, arg: tfsl.languages.Language):
        return tfsl.monolingualtextholder.MonolingualTextHolder.__getitem__(self, arg)

    @getitem.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return tfsl.monolingualtextholder.MonolingualTextHolder.__getitem__(self, arg)

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
        raise KeyError(f"Can't check for {type(arg)} in LexemeSense")

    @contains.register
    def _(self, arg: tfsl.languages.Language):
        return tfsl.monolingualtextholder.MonolingualTextHolder.__contains__(self, arg)

    @contains.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return tfsl.monolingualtextholder.MonolingualTextHolder.__contains__(self, arg)

    @contains.register(tfsl.claim.Claim)
    @contains.register(str)
    def _(self, arg: Union[str, tfsl.claim.Claim]):
        return tfsl.statementholder.StatementHolder.__contains__(self, arg)

    def __eq__(self, rhs):
        glosses_equal = tfsl.monolingualtextholder.MonolingualTextHolder.__eq__(self, rhs)
        statements_equal = tfsl.statementholder.StatementHolder.__eq__(self, rhs)
        return glosses_equal and statements_equal

    def __str__(self):
        # TODO: output everything else
        gloss_str = tfsl.monolingualtextholder.MonolingualTextHolder.__str__(self)
        stmt_str = tfsl.statementholder.StatementHolder.__str__(self)
        return "\n".join([gloss_str, stmt_str])

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
