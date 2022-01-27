from copy import deepcopy
from functools import singledispatchmethod

import tfsl.languages
import tfsl.monolingualtext
import tfsl.monolingualtextholder
import tfsl.statement
import tfsl.statementholder
import tfsl.utils

class LexemeForm:
    def __init__(self, representations, features=None, statements=None):
        super().__init__()
        self.representations = tfsl.monolingualtextholder.MonolingualTextHolder(representations)
        self.statements = tfsl.statementholder.StatementHolder(statements)

        if features is None:
            self.features = set()
        elif isinstance(features, str):
            self.features = set([features])
        else:
            self.features = deepcopy(features)

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
        return self.statements[arg]

    @getitem.register(tfsl.monolingualtext.MonolingualText)
    @getitem.register(tfsl.languages.Language)
    def _(self, arg: tfsl.monolingualtextholder.lang_or_mt):
        return self.representations[arg]

    def __add__(self, arg):
        return self.add(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {type(arg)} to LexemeForm")

    @add.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        published_settings = self.get_published_settings()
        form_out = LexemeForm(self.representations + arg, self.features, self.statements)
        form_out.set_published_settings(published_settings)
        return form_out

    @add.register
    def _(self, arg: str):
        published_settings = self.get_published_settings()
        form_out = LexemeForm(self.representations, self.features | set(arg), self.statements)
        form_out.set_published_settings(published_settings)
        return form_out

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        published_settings = self.get_published_settings()
        form_out = LexemeForm(self.representations, self.features, self.statements + arg)
        form_out.set_published_settings(published_settings)
        return form_out

    def __sub__(self, arg):
        return self.sub(arg)

    @singledispatchmethod
    def sub(self, arg):
        raise NotImplementedError(f"Can't subtract {type(arg)} from LexemeForm")

    @sub.register(tfsl.languages.Language)
    @sub.register(tfsl.monolingualtext.MonolingualText)
    def _(self, arg: tfsl.monolingualtextholder.lang_or_mt):
        published_settings = self.get_published_settings()
        form_out = LexemeForm(self.representations - arg, self.features, self.statements)
        form_out.set_published_settings(published_settings)
        return form_out

    @sub.register
    def _(self, arg: str):
        published_settings = self.get_published_settings()
        if tfsl.utils.matches_item(arg):
            form_out = LexemeForm(self.representations, self.features - set([arg]), self.statements)
        elif tfsl.utils.matches_property(arg):
            form_out = LexemeForm(self.representations, self.features, self.statements - arg)
        form_out.set_published_settings(published_settings)
        return form_out

    @sub.register
    def _(self, arg: tfsl.statement.Statement):
        published_settings = self.get_published_settings()
        form_out = LexemeForm(self.representations, self.features, self.statements - arg)
        form_out.set_published_settings(published_settings)
        return form_out

    def __contains__(self, arg):
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg):
        raise KeyError(f"Can't check for {type(arg)} in LexemeForm")

    @contains.register(tfsl.languages.Language)
    @contains.register(tfsl.monolingualtext.MonolingualText)
    def _(self, arg: tfsl.monolingualtextholder.lang_or_mt):
        return arg in self.representations

    @contains.register
    def _(self, arg: tfsl.claim.Claim):
        return arg in self.statements

    @contains.register
    def _(self, arg: str):
        try:
            return arg in self.statements
        except TypeError as e:
            if tfsl.utils.matches_item(arg):
                return arg in self.features
            raise e

    def __eq__(self, rhs):
        representations_equal = self.representations == rhs.representations
        features_equal = self.features == rhs.features
        statements_equal = self.statements == rhs.statements
        return representations_equal and features_equal and statements_equal

    def __str__(self):
        base_str = str(self.representations)
        feat_str = ': '+', '.join(self.features)
        stmt_str = str(self.statements)
        return "\n".join([base_str + feat_str, stmt_str])

    def __jsonout__(self):
        reps_dict = self.representations.__jsonout__()
        base_dict = {"representations": reps_dict, "grammaticalFeatures": self.features}

        if self.id is not None:
            base_dict["id"] = self.id
        else:
            base_dict["add"] = ""

        if (statement_dict := self.statements.__jsonout__()):
            base_dict["claims"] = statement_dict

        return base_dict

def build_form(form_in):
    reps = tfsl.monolingualtextholder.build_text_list(form_in["representations"])
    feats = form_in["grammaticalFeatures"]
    claims = tfsl.statementholder.build_statement_list(form_in["claims"])

    form_out = LexemeForm(reps, feats, claims)
    form_out.set_published_settings(form_in)

    return form_out
