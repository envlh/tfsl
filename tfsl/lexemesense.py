from collections import defaultdict
from copy import deepcopy
from functools import singledispatchmethod
from textwrap import indent

import tfsl.monolingualtext
import tfsl.statement
import tfsl.utils


class LexemeSense:
    def __init__(self, glosses, statements=None):
        if isinstance(glosses, tfsl.monolingualtext.MonolingualText):
            self.glosses = [glosses.text @ glosses.language]
        else:
            self.glosses = deepcopy(glosses)

        # TODO: split statement dict handling off someplace else?
        if statements is None:
            self.statements = defaultdict(list)
        elif isinstance(statements, list):
            self.statements = defaultdict(list)
            for arg in statements:
                self.statements[arg.property].append(arg)
        else:
            self.statements = deepcopy(statements)

        self.id = None

    def __getitem__(self, key):
        id_matches_key = lambda obj: obj.id == key

        if tfsl.utils.matches_property(key):
            return self.statements.get(key, [])
        raise KeyError

    def __add__(self, arg):
        return self.add(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {type(arg)} to LexemeSense")

    def __sub__(self, arg):
        return self.sub(arg)

    @singledispatchmethod
    def sub(self, arg):
        raise NotImplementedError(f"Can't subtract {type(arg)} from LexemeForm")

    @add.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return LexemeSense(tfsl.utils.add_to_mtlist(self.glosses, arg), self.statements)

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        return LexemeSense(self.glosses, tfsl.utils.add_claimlike(self.statements, arg))

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
        return self.glosses == rhs.glosses and self.statements == rhs.statements

    def __str__(self):
        # TODO: output everything else
        base_str = ' / '.join([str(gloss) for gloss in self.glosses])
        stmt_str = ""
        if self.statements != {}:
            stmt_str = "\n<\n"+indent("\n".join([str(stmt) for prop in self.statements for stmt in self.statements[prop]]), tfsl.utils.DEFAULT_INDENT)+"\n>"
        return base_str + stmt_str

    def __jsonout__(self):
        glosses_dict = {gloss.language.code: {"value": gloss.text, "language": gloss.language.code} for gloss in self.glosses}
        base_dict = {"glosses": glosses_dict}
        if self.id is not None:
            base_dict["id"] = self.id
        else:
            base_dict["add"] = ""
        base_dict["claims"] = defaultdict(list)
        for stmtprop, stmtval in self.statements.items():
            base_dict["claims"][stmtprop].extend([stmt.__jsonout__() for stmt in stmtval])
        if base_dict["claims"] == {}:
            del base_dict["claims"]
        else:
            base_dict["claims"] = dict(base_dict["claims"])
        return base_dict


def build_sense(sense_in):
    glosses = []
    for code, gloss in sense_in["glosses"].items():
        new_gloss = gloss["value"] @ tfsl.languages.get_first_lang(gloss["language"])
        glosses.append(new_gloss)

    claims = defaultdict(list)
    claims_in = sense_in["claims"]
    for prop in claims_in:
        for claim in claims_in[prop]:
            claims[prop].append(tfsl.statement.build_statement(claim))

    sense_out = LexemeSense(glosses, claims)
    sense_out.id = sense_in["id"]
    return sense_out
