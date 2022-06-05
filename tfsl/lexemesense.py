from functools import singledispatchmethod
from typing import Union

import tfsl.monolingualtext
import tfsl.monolingualtextholder
import tfsl.statement
import tfsl.statementholder
import tfsl.utils

class LexemeSense:
    def __init__(self, glosses, statements=None):
        super().__init__()
        if isinstance(glosses, tfsl.monolingualtextholder.MonolingualTextHolder):
            self.glosses = glosses
        else:
            self.glosses = tfsl.monolingualtextholder.MonolingualTextHolder(glosses)
        
        if isinstance(statements, tfsl.statementholder.StatementHolder):
            self.statements = statements
        else:
            self.statements = tfsl.statementholder.StatementHolder(statements)

        self.id = None

    def get_published_settings(self):
        return {
            "id": self.id
        }

    def set_published_settings(self, sense_in):
        self.id = sense_in["id"]

    def __getitem__(self, arg):
        return self.getitem(arg)

    @singledispatchmethod
    def getitem(self, arg):
        raise KeyError(f"Can't get {type(arg)} from LexemeSense")

    @getitem.register
    def _(self, arg: str):
        return self.statements[arg]

    @getitem.register(tfsl.monolingualtext.MonolingualText)
    @getitem.register(tfsl.languages.Language)
    def _(self, arg: tfsl.monolingualtextholder.lang_or_mt):
        return self.glosses[arg]

    def haswbstatement(self, property_in, value_in=None):
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        return self.statements.haswbstatement(property_in, value_in)

    def __add__(self, arg):
        return self.add(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {type(arg)} to LexemeSense")

    @add.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        published_settings = self.get_published_settings()
        sense_out = LexemeSense(self.glosses + arg, self.statements)
        sense_out.set_published_settings(published_settings)
        return sense_out

    @add.register
    def _(self, arg: tfsl.statement.Statement):
        published_settings = self.get_published_settings()
        sense_out = LexemeSense(self.glosses, self.statements + arg)
        sense_out.set_published_settings(published_settings)
        return sense_out

    def __sub__(self, arg):
        return self.sub(arg)

    @singledispatchmethod
    def sub(self, arg):
        raise NotImplementedError(f"Can't subtract {type(arg)} from LexemeSense")

    @sub.register(tfsl.languages.Language)
    @sub.register(tfsl.monolingualtext.MonolingualText)
    def _(self, arg: tfsl.monolingualtextholder.lang_or_mt):
        published_settings = self.get_published_settings()
        sense_out = LexemeSense(self.glosses - arg, self.statements)
        sense_out.set_published_settings(published_settings)
        return sense_out

    @sub.register
    def _(self, arg: str):
        published_settings = self.get_published_settings()
        if tfsl.utils.matches_property(arg):
            sense_out = LexemeSense(self.glosses, self.statements - arg)
        sense_out.set_published_settings(published_settings)
        return sense_out

    @sub.register
    def _(self, arg: tfsl.statement.Statement):
        published_settings = self.get_published_settings()
        sense_out = LexemeSense(self.glosses, self.statements - arg)
        sense_out.set_published_settings(published_settings)
        return sense_out

    def __contains__(self, arg):
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg):
        raise KeyError(f"Can't check for {type(arg)} in LexemeSense")

    @contains.register(tfsl.languages.Language)
    @contains.register(tfsl.monolingualtext.MonolingualText)
    def _(self, arg: tfsl.monolingualtextholder.lang_or_mt):
        return arg in self.glosses

    @contains.register(tfsl.statement.Statement)
    @contains.register(tfsl.claim.Claim)
    @contains.register(str)
    def _(self, arg: Union[str, tfsl.claim.Claim, tfsl.statement.Statement]):
        return arg in self.statements

    def __eq__(self, rhs):
        glosses_equal = self.glosses == rhs.glosses
        statements_equal = self.statements == rhs.statements
        return glosses_equal and statements_equal

    def __str__(self):
        # TODO: output everything else
        gloss_str = str(self.glosses)
        stmt_str = str(self.statements)
        return "\n".join([gloss_str, stmt_str])

    def __jsonout__(self):
        glosses_dict = self.glosses.__jsonout__()
        base_dict = {"glosses": glosses_dict}

        if self.id is not None:
            base_dict["id"] = self.id
        else:
            base_dict["add"] = ""

        if (statement_dict := self.statements.__jsonout__()):
            base_dict["claims"] = statement_dict

        return base_dict

def build_sense(sense_in):
    glosses = tfsl.monolingualtextholder.build_text_list(sense_in["glosses"])
    statements = tfsl.statementholder.build_statement_list(sense_in["claims"])

    sense_out = LexemeSense(glosses, statements)
    sense_out.id = sense_in["id"]
    return sense_out
