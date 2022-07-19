from copy import deepcopy
from functools import singledispatchmethod
from typing import Dict, List, Optional, Sequence, Set, Union

import tfsl.interfaces as I
import tfsl.languages
import tfsl.monolingualtext
import tfsl.monolingualtextholder
import tfsl.statement
import tfsl.statementholder
import tfsl.utils

class LexemeForm:
    def __init__(self,
                 representations: Union[tfsl.monolingualtextholder.MonolingualTextHolder,
                                        tfsl.monolingualtext.MonolingualText,
                                        List[tfsl.monolingualtext.MonolingualText]],
                 features: Optional[Union[List[I.Qid], Set[I.Qid]]]=None,
                 statements: Optional[Union[
                    tfsl.statementholder.StatementHolder,
                    I.StatementSet,
                    List[tfsl.statement.Statement]
                 ]]=None):
        super().__init__()

        self.representations: tfsl.monolingualtextholder.MonolingualTextHolder
        if isinstance(representations, tfsl.monolingualtextholder.MonolingualTextHolder):
            self.representations = representations
        else:
            self.representations = tfsl.monolingualtextholder.MonolingualTextHolder(representations)
        
        self.statements: tfsl.statementholder.StatementHolder
        if isinstance(statements, tfsl.statementholder.StatementHolder):
            self.statements = statements
        else:
            self.statements = tfsl.statementholder.StatementHolder(statements)

        self.features: Set[I.Qid]
        if features is None:
            self.features = set()
        else:
            self.features = set(features)

        self.id: Optional[str] = None

    def get_published_settings(self) -> I.LexemeFormPublishedSettings:
        if self.id is not None:
            return {
                "id": self.id
            }
        return {}

    def set_published_settings(self, form_in: I.LexemeFormPublishedSettings) -> None:
        self.id = form_in["id"]

    def __getitem__(self, arg: object) -> Union[List[tfsl.statement.Statement], tfsl.monolingualtext.MonolingualText]:
        return self.getitem(arg)

    @singledispatchmethod
    def getitem(self, arg: object) -> Union[List[tfsl.statement.Statement], tfsl.monolingualtext.MonolingualText]:
        raise KeyError(f"Can't get {type(arg)} from LexemeForm")

    @getitem.register
    def _(self, arg: str) -> List[tfsl.statement.Statement]:
        return self.statements[arg]

    @getitem.register(tfsl.monolingualtext.MonolingualText)
    @getitem.register(tfsl.languages.Language)
    def _(self, arg: tfsl.monolingualtextholder.lang_or_mt) -> tfsl.monolingualtext.MonolingualText:
        return self.representations[arg]

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return self.statements.haswbstatement(property_in, value_in)

    def __add__(self, arg: object) -> 'LexemeForm':
        if isinstance(arg, tfsl.monolingualtext.MonolingualText):
            published_settings = self.get_published_settings()
            form_out = LexemeForm(self.representations + arg, self.features, self.statements)
            form_out.set_published_settings(published_settings)
            return form_out
        elif isinstance(arg, str):
            published_settings = self.get_published_settings()
            if I.is_Qid(arg):
                form_out = LexemeForm(self.representations, self.features | set([arg]), self.statements)
            form_out.set_published_settings(published_settings)
            return form_out
        elif isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            form_out = LexemeForm(self.representations, self.features, self.statements + arg)
            form_out.set_published_settings(published_settings)
            return form_out
        raise NotImplementedError(f"Can't add {type(arg)} to LexemeForm")

    def __sub__(self, arg: object) -> 'LexemeForm':
        if isinstance(arg, tfsl.languages.Language) or isinstance(arg, tfsl.monolingualtext.MonolingualText):
            published_settings = self.get_published_settings()
            form_out = LexemeForm(self.representations - arg, self.features, self.statements)
            form_out.set_published_settings(published_settings)
            return form_out
        elif isinstance(arg, str):
            published_settings = self.get_published_settings()
            if I.is_Qid(arg):
                form_out = LexemeForm(self.representations, self.features - set([arg]), self.statements)
            elif I.is_Pid(arg):
                form_out = LexemeForm(self.representations, self.features, self.statements - arg)
            form_out.set_published_settings(published_settings)
            return form_out
        elif isinstance(arg, tfsl.statement.Statement):
            published_settings = self.get_published_settings()
            form_out = LexemeForm(self.representations, self.features, self.statements - arg)
            form_out.set_published_settings(published_settings)
            return form_out
        raise NotImplementedError(f"Can't subtract {type(arg)} from LexemeForm")

    def __contains__(self, arg: object) -> bool:
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg: object) -> bool:
        raise KeyError(f"Can't check for {type(arg)} in LexemeForm")

    @contains.register(tfsl.languages.Language)
    @contains.register(tfsl.monolingualtext.MonolingualText)
    def _(self, arg: tfsl.monolingualtextholder.lang_or_mt) -> bool:
        return arg in self.representations

    @contains.register
    def _(self, arg: tfsl.claim.Claim) -> bool:
        return arg in self.statements

    @contains.register
    def _(self, arg: str) -> bool:
        try:
            return arg in self.statements
        except TypeError as e:
            if tfsl.utils.matches_item(arg):
                return arg in self.features
            raise e

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, LexemeForm):
            return NotImplemented
        representations_equal = self.representations == rhs.representations
        features_equal = self.features == rhs.features
        statements_equal = self.statements == rhs.statements
        return representations_equal and features_equal and statements_equal

    def __str__(self) -> str:
        base_str = str(self.representations)
        feat_str = ': '+', '.join(self.features)
        stmt_str = str(self.statements)
        return "\n".join([base_str + feat_str, stmt_str])

    def __jsonout__(self) -> I.LexemeFormDict:
        reps_dict = self.representations.__jsonout__()
        base_dict: I.LexemeFormDict = {"representations": reps_dict, "grammaticalFeatures": list(self.features)}

        if self.id is not None:
            base_dict["id"] = self.id
        else:
            base_dict["add"] = ""

        if (statement_dict := self.statements.__jsonout__()):
            base_dict["claims"] = statement_dict

        return base_dict

def build_form(form_in: I.LexemeFormDict) -> LexemeForm:
    reps = tfsl.monolingualtextholder.build_text_list(form_in["representations"])
    feats = form_in["grammaticalFeatures"]
    claims = tfsl.statementholder.build_statement_list(form_in["claims"])

    form_out = LexemeForm(reps, feats, claims)
    form_out.set_published_settings(form_in)

    return form_out
