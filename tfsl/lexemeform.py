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
            self.representations = [representations.text @ representations.language]
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
        return LexemeForm(tfsl.utils.add_to_mtlist(self.representations, arg), self.features, self.statements)

    @add.register
    def _(self, arg: str):
        return LexemeForm(self.representations, tfsl.utils.add_to_list(self.features, arg), self.statements)

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        return LexemeForm(self.representations, self.features, tfsl.utils.add_claimlike(self.statements, arg))

    @sub.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return LexemeForm(tfsl.utils.sub_from_list(self.representations, arg), self.features, self.statements)

    @sub.register
    def _(self, arg: tfsl.languages.Language):
        return LexemeForm(tfsl.utils.remove_replang(self.representations, arg), self.features, self.statements)

    @sub.register
    def _(self, arg: str):
        if(tfsl.utils.matches_item(arg)):
            return LexemeForm(self.representations, tfsl.utils.sub_from_list(self.features, arg), self.statements)
        elif(tfsl.utils.matches_property(arg)):
            return LexemeForm(self.representations, self.features, tfsl.utils.sub_property(self.statements, arg))

    @sub.register
    def _(self, arg: tfsl.statement.Statement):
        return LexemeForm(self.representations, self.features, tfsl.utils.sub_claimlike(self.statements, arg))

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
        return self.representations == rhs.representations and self.features == rhs.features and self.statements == rhs.statements

    def __str__(self):
        base_str = '/'.join([str(rep) for rep in self.representations])
        feat_str = ': '+', '.join(self.features)
        stmt_str = ""
        if(self.statements != {}):
            stmt_str = "\n<\n"+indent("\n".join([str(stmt) for stmt in self.statements]), tfsl.utils.default_indent)+"\n>"
        return base_str + feat_str + stmt_str

    def __jsonout__(self):
        reps_dict = {rep.language.code: {"value": rep.text, "language": rep.language.code} for rep in self.representations}
        base_dict = {"representations": reps_dict, "grammaticalFeatures": self.features}
        try:
            base_dict["id"] = self.id
        except AttributeError:
            base_dict["add"] = ""
        base_dict["claims"] = self.statements
        if(base_dict["claims"] == {}):
            del base_dict["claims"]
        return base_dict
