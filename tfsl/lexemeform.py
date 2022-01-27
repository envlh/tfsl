from copy import deepcopy
from functools import singledispatchmethod

import tfsl.languages
import tfsl.monolingualtext
import tfsl.monolingualtextholder
import tfsl.statement
import tfsl.statementholder
import tfsl.utils

class LexemeForm(
    tfsl.monolingualtextholder.MonolingualTextHolder,
    tfsl.statementholder.StatementHolder
):
    def __init__(self, representations, features=None, statements=None):
        super().__init__(texts=representations, statements=statements)

        if features is None:
            self.features = []
        elif isinstance(features, str):
            self.features = [features]
        else:
            self.features = deepcopy(features)

        self.representations = self.texts
        self.removed_representations = self.removed_texts
        self.id = None

    def get_published_settings(self):
        return {
            "id": self.id
        }

    def set_published_settings(self, form_in):
        self.id = form_in["id"]

    def __getitem__(self, arg):
        return self.getitem(arg)

    @singledispatchmethod
    def getitem(self, arg):
        raise KeyError(f"Can't get {type(arg)} from LexemeForm")

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
        published_settings = self.get_published_settings()
        form_out = LexemeForm(self.representations,
                          self.features,
                          tfsl.utils.add_claimlike(self.statements, arg))
        form_out.set_published_settings(published_settings)
        return form_out

    @sub.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        published_settings = self.get_published_settings()
        form_out = LexemeForm(tfsl.utils.sub_from_list(self.representations, arg),
                          self.features,
                          self.statements)
        form_out.set_published_settings(published_settings)
        form_out.removed_representations.append(arg)
        return form_out

    @sub.register
    def _(self, arg: tfsl.languages.Language):
        return LexemeForm(tfsl.utils.remove_replang(self.representations, arg),
                          self.features,
                          self.statements)

    @sub.register
    def _(self, arg: str):
        if tfsl.utils.matches_item(arg):
            return LexemeForm(self.representations,
                              tfsl.utils.sub_from_list(self.features, arg),
                              self.statements)
        elif tfsl.utils.matches_property(arg):
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
        raise KeyError(f"Can't check for {type(arg)} in LexemeForm")

    @contains.register
    def _(self, arg: tfsl.languages.Language):
        return tfsl.monolingualtextholder.MonolingualTextHolder.__contains__(self, arg)

    @contains.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return tfsl.monolingualtextholder.MonolingualTextHolder.__contains__(self, arg)

    @contains.register
    def _(self, arg: tfsl.claim.Claim):
        return tfsl.statementholder.StatementHolder.__contains__(self, arg)

    @contains.register
    def _(self, arg: str):
        try:
            return tfsl.statementholder.StatementHolder.__contains__(self, arg)
        except TypeError as e:
            if tfsl.utils.matches_item(arg):
                return arg in self.features
            raise e

    def __eq__(self, rhs):
        reps_equal = tfsl.monolingualtextholder.MonolingualTextHolder.__eq__(self, rhs)
        stmts_equal = tfsl.statementholder.StatementHolder.__eq__(self, rhs)
        feats_equal = (self.features == rhs.features)
        return reps_equal and feats_equal and stmts_equal

    def __str__(self):
        base_str = tfsl.statementholder.StatementHolder.__str__(self)
        feat_str = ': '+', '.join(self.features)
        stmt_str = tfsl.statementholder.StatementHolder.__str__(self)
        return "\n".join([base_str + feat_str, stmt_str])

    def __jsonout__(self):
        reps_dict = self.build_text_dict()
        base_dict = {"representations": reps_dict, "grammaticalFeatures": self.features}

        if self.id is not None:
            base_dict["id"] = self.id
        else:
            base_dict["add"] = ""

        if (statement_dict := self.build_statement_dict()):
            base_dict["claims"] = statement_dict

        return base_dict

def build_form(form_in):
    reps = tfsl.monolingualtextholder.build_text_list(form_in["representations"])
    feats = form_in["grammaticalFeatures"]
    claims = tfsl.statementholder.build_statement_list(form_in["claims"])

    form_out = LexemeForm(reps, feats, claims)
    form_out.set_published_settings(form_in)

    return form_out
