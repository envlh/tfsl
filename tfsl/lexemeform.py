from collections import defaultdict
from copy import deepcopy
from functools import singledispatchmethod
from textwrap import indent

import tfsl.monolingualtext
import tfsl.statement
import tfsl.utils


class LexemeForm:
    def __init__(self, representations, features=[], statements=[]):
        if(type(representations) == tfsl.monolingualtext.MonolingualText):
            self.representations = [representations]
        else:
            self.representations = deepcopy(representations)

        if(type(features) == str):
            self.features = [features]
        else:
            self.features = deepcopy(features)

        if(type(statements) == list):
            self.statements = defaultdict(list)
            for arg in statements:
                self.statements[arg.property].append(arg)
        else:
            self.statements = deepcopy(statements)

    def __add__(self, arg):
        return self.add(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {type(arg)} to LexemeForm")

    def __sub__(self, arg):
        return self.sub(arg)

    @singledispatchmethod
    def sub(self, arg):
        raise NotImplementedError(f"Can't subtract {type(arg)} from LexemeForm")

    @add.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return LexemeForm(tfsl.utils.add_to_mtlist(self.representations, arg),
                          self.features,
                          self.statements)

    @add.register
    def _(self, arg: str):
        return LexemeForm(self.representations,
                          tfsl.utils.add_to_list(self.features, arg),
                          self.statements)

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        return LexemeForm(self.representations,
                          self.features,
                          tfsl.utils.add_claimlike(self.statements, arg))

    @sub.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return LexemeForm(tfsl.utils.sub_from_list(self.representations, arg),
                          self.features,
                          self.statements)

    @sub.register
    def _(self, arg: tfsl.languages.Language):
        return LexemeForm(tfsl.utils.remove_replang(self.representations, arg),
                          self.features,
                          self.statements)

    @sub.register
    def _(self, arg: str):
        if(tfsl.utils.matches_item(arg)):
            return LexemeForm(self.representations,
                              tfsl.utils.sub_from_list(self.features, arg),
                              self.statements)
        elif(tfsl.utils.matches_property(arg)):
            return LexemeForm(self.representations,
                              self.features,
                              tfsl.utils.sub_property(self.statements, arg))

    @sub.register
    def _(self, arg: tfsl.statement.Statement):
        return LexemeForm(self.representations,
                          self.features,
                          tfsl.utils.sub_claimlike(self.statements, arg))

    def __contains__(self, arg):
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg):
        return arg in self.statements[arg.property]

    @contains.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return arg in self.representations

    @contains.register
    def _(self, arg: str):
        if(tfsl.utils.matches_property(arg)):
            return arg in self.statements
        elif(tfsl.utils.matches_item(arg)):
            return arg in self.features

    @contains.register
    def _(self, arg: tfsl.claim.Claim):
        for prop in self.statements:
            if arg in self.statements[prop]:
                return True
        return False

    @contains.register
    def _(self, arg: tfsl.languages.Language):
        for rep in self.representations:
            if(rep.language == arg):
                return True
        return False

    def __eq__(self, rhs):
        reps_equal = (self.representations == rhs.representations)
        feats_equal = (self.features == rhs.features)
        stmts_equal = (self.statements == rhs.statements)
        return reps_equal and feats_equal and stmts_equal

    def __str__(self):
        base_str = '/'.join([str(rep) for rep in self.representations])
        feat_str = ': '+', '.join(self.features)

        stmt_str = ""
        if(self.statements != {}):
            prefix = "\n<\n"
            suffix = "\n>"
            stmt_strings = [str(stmt) for prop in self.statements for stmt in self.statements[prop]]
            stmts = indent("\n".join(stmt_strings), tfsl.utils.default_indent)
            stmt_str = prefix + stmts + suffix

        return base_str + feat_str + stmt_str

    def __jsonout__(self):
        reps_dict = {}
        for rep in self.representations:
            reps_dict[rep.language.code] = {"value": rep.text, "language": rep.language.code}
        base_dict = {"representations": reps_dict, "grammaticalFeatures": self.features}
        try:
            base_dict["id"] = self.id
        except AttributeError:
            base_dict["add"] = ""
        base_dict["claims"] = defaultdict(list)
        for stmtprop, stmtval in self.statements.items():
            base_dict["claims"][stmtprop].extend([stmt.__jsonout__() for stmt in stmtval])
        if(base_dict["claims"] == {}):
            del base_dict["claims"]
        else:
            base_dict["claims"] = dict(base_dict["claims"])
        return base_dict


def build_form(form_in):
    reps = []
    for code, rep in form_in["representations"].items():
        new_rep = rep["value"] @ tfsl.languages.get_first_lang(rep["language"])
        reps.append(new_rep)

    feats = form_in["grammaticalFeatures"]

    claims = defaultdict(list)
    claims_in = form_in["claims"]
    for prop in claims_in:
        for claim in claims_in[prop]:
            claims[prop].append(tfsl.statement.build_statement(claim))

    form_out = LexemeForm(reps, feats, claims)
    form_out.id = form_in["id"]
    return form_out
