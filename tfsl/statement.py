from collections import defaultdict
from copy import deepcopy
from enum import Enum
from functools import singledispatchmethod
from textwrap import indent

import tfsl.claim
import tfsl.reference
import tfsl.utils


class Rank(Enum):
    Preferred = 1
    Normal = 0
    Deprecated = -1


class Statement:
    """ Represents a statement, or a claim with accompanying rank, optional qualifiers,
        and optional references.
    """
    def __init__(self, property_in: str,
                 value_in,
                 rank=Rank.Normal,
                 qualifiers=[],
                 references=[]):
        self.property = property_in
        self.value = deepcopy(value_in)
        self.rank = rank

        if(type(qualifiers) == list):
            self.qualifiers = defaultdict(list)
            for arg in qualifiers:
                self.qualifiers[arg.property].append(arg)
        else:
            self.qualifiers = deepcopy(qualifiers)

        self.references = deepcopy(references)

    def __add__(self, arg):
        return self.add(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {str(type(arg))} to statement")

    @add.register
    def _(self, arg: tfsl.claim.Claim):
        return Statement(self.property, self.value, self.rank, tfsl.utils.add_claimlike(self.qualifiers, arg), self.references)

    @add.register
    def _(self, arg: tfsl.reference.Reference):
        return Statement(self.property, self.value, self.rank, self.qualifiers, tfsl.utils.add_to_list(self.references, arg))

    def __sub__(self, arg):
        return self.sub(arg)

    @singledispatchmethod
    def sub(self, arg):
        raise NotImplementedError(f"Can't subtract {str(type(arg))} from statement")

    @sub.register
    def _(self, arg: tfsl.claim.Claim):
        return Statement(self.property, self.value, self.rank, tfsl.utils.sub_claimlike(self.qualifiers, arg), self.references)

    @sub.register
    def _(self, arg: tfsl.reference.Reference):
        return Statement(self.property, self.value, self.rank, self.qualifiers, tfsl.utils.sub_from_list(self.references, arg))

    def __matmul__(self, arg):
        return self.matmul(arg)

    @singledispatchmethod
    def matmul(self, arg):
        raise NotImplementedError(f"{str(type(arg))} is not a rank")

    @matmul.register
    def matmul(self, arg: Rank):
        if(arg == self.rank):
            return self
        return Statement(self.property, self.value, arg, self.qualifiers, self.references)

    def __eq__(self, rhs):
        return self.property == rhs.property and self.value == rhs.value and self.rank == rhs.rank and self.qualifiers == rhs.qualifiers and self.references == rhs.references

    def __str__(self):
        # TODO: output everything else
        base_str = f'{self.property}: {self.value} ({self.rank})'
        qualifiers_str = ""
        references_str = ""

        if self.qualifiers != {}:
            qualifiers_str = "(\n" + indent("\n".join([str(qual) for key in self.qualifiers for qual in self.qualifiers[key]]), tfsl.utils.DEFAULT_INDENT) + "\n)"
        if len(self.references) != 0:
            references_str = "[\n" + indent("\n".join([str(ref) for ref in self.references]), tfsl.utils.DEFAULT_INDENT) + "\n]"
        return base_str + qualifiers_str + references_str

    def __jsonout__(self):
        base_dict = {"type": "statement", "mainsnak": tfsl.claim.Claim(self.property, self.value).__jsonout__()}
        try:
            base_dict["id"] = self.id
        except AttributeError:
            pass
        base_dict["rank"] = ["deprecated", "normal", "preferred"][self.rank.value+1]
        base_dict["qualifiers"] = defaultdict(list)
        for stmtprop, stmtval in self.qualifiers.items():
            base_dict["qualifiers"][stmtprop].extend([stmt.__jsonout__() for stmt in stmtval])
        if(base_dict["qualifiers"] == {}):
            del base_dict["qualifiers"]
        else:
            base_dict["qualifiers"] = dict(base_dict["qualifiers"])
        base_dict["qualifiers-order"] = list(self.qualifiers.keys())
        if(base_dict["qualifiers-order"] == []):
            del base_dict["qualifiers-order"]
        base_dict["references"] = [reference.__jsonout__() for reference in self.references]
        return base_dict


def build_quals(quals_in):
    if(quals_in is None):
        return []
    quals = defaultdict(list)
    for prop in quals_in:
        for qual in quals_in[prop]:
            quals[prop].append(tfsl.claim.build_claim(qual))
    return quals


def build_statement(stmt_in):
    stmt_rank = Rank.Normal
    if(stmt_in["rank"] == 'preferred'):
        stmt_rank = Rank.Preferred
    elif(stmt_in["rank"] == 'deprecated'):
        stmt_rank = Rank.Deprecated

    stmt_mainsnak = stmt_in["mainsnak"]
    stmt_property = stmt_mainsnak["property"]
    stmt_datatype = stmt_mainsnak["datatype"]
    stmt_value = tfsl.claim.build_value(stmt_mainsnak["datavalue"])
    stmt_quals = build_quals(stmt_in.get("qualifiers", None))
    stmt_refs = []
    if(stmt_in.get("references", False)):
        stmt_refs = [tfsl.reference.build_ref(ref) for ref in stmt_in["references"]]

    stmt_out = Statement(stmt_property, stmt_value, stmt_rank, stmt_quals, stmt_refs)
    stmt_out.id = stmt_in["id"]
    stmt_out.qualifiers_order = stmt_in.get("qualifiers-order", None)
    return stmt_out
