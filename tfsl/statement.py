from collections import defaultdict
from copy import deepcopy
from enum import Enum
from functools import singledispatchmethod
from textwrap import indent
from typing import DefaultDict, List, Optional, Union

import tfsl.interfaces as I
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
    def __init__(self,
                 property_in: I.Pid,
                 value_in: I.ClaimValue,
                 rank: Optional[Rank]=None,
                 qualifiers: Optional[Union[List[tfsl.claim.Claim], tfsl.reference.ClaimSet]]=None,
                 references: Optional[List[tfsl.reference.Reference]]=None):
        self.rank: Rank
        if rank is None:
            self.rank = Rank.Normal
        else:
            self.rank = rank

        self.property: I.Pid = property_in
        self.value: I.ClaimValue = deepcopy(value_in)

        self.qualifiers: tfsl.reference.ClaimSet = tfsl.reference.ClaimSet()

        if isinstance(qualifiers, tfsl.reference.ClaimSet):
            for prop in qualifiers:
                for claim in qualifiers[prop]:
                    self.qualifiers = self.qualifiers.add(claim)
        elif qualifiers is not None:
            for arg in qualifiers:
                self.qualifiers = self.qualifiers.add(arg)

        self.references: List[tfsl.reference.Reference]
        if references is None:
            self.references = []
        else:
            self.references = deepcopy(references)

        self.id: Optional[str] = None
        self.qualifiers_order: Optional[List[I.Pid]] = None

    def __getitem__(self, key):
        id_matches_key = lambda obj: obj.id == key

        if tfsl.utils.matches_property(key):
            return self.qualifiers.get(key, [])
        raise KeyError

    def __add__(self, arg):
        return self.add(arg)

    @singledispatchmethod
    def add(self, arg):
        raise NotImplementedError(f"Can't add {str(type(arg))} to statement")

    @add.register
    def _(self, arg: tfsl.claim.Claim):
        return Statement(self.property, self.value, self.rank, self.qualifiers.add(arg), self.references)

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
        return Statement(self.property, self.value, self.rank, self.qualifiers.sub(arg), self.references)

    @sub.register
    def _(self, arg: tfsl.reference.Reference):
        return Statement(self.property, self.value, self.rank, self.qualifiers, tfsl.utils.sub_from_list(self.references, arg))

    def __matmul__(self, arg):
        return self.matmul(arg)

    @singledispatchmethod
    def matmul(self, arg):
        raise NotImplementedError(f"{str(type(arg))} is not a rank")

    @matmul.register
    def _(self, arg: Rank):
        if arg == self.rank:
            return self
        return Statement(self.property, self.value, arg, self.qualifiers, self.references)

    def __eq__(self, rhs):
        return self.property == rhs.property and self.value == rhs.value and self.rank == rhs.rank and self.qualifiers == rhs.qualifiers and self.references == rhs.references

    def set_published_settings(self, stmt_in):
        self.id = stmt_in["id"]
        self.qualifiers_order = stmt_in.get("qualifiers-order", None)

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
        if base_dict["qualifiers"] == {}:
            del base_dict["qualifiers"]
        else:
            base_dict["qualifiers"] = dict(base_dict["qualifiers"])
        base_dict["qualifiers-order"] = list(self.qualifiers.keys())
        if base_dict["qualifiers-order"] == []:
            del base_dict["qualifiers-order"]
        base_dict["references"] = [reference.__jsonout__() for reference in self.references]
        return base_dict


def build_quals(quals_in):
    if quals_in is None:
        return []
    quals = defaultdict(list)
    for prop in quals_in:
        for qual in quals_in[prop]:
            quals[prop].append(tfsl.claim.build_claim(qual))
    return quals


def build_statement(stmt_in):
    stmt_rank = Rank.Normal
    if stmt_in["rank"] == 'preferred':
        stmt_rank = Rank.Preferred
    elif stmt_in["rank"] == 'deprecated':
        stmt_rank = Rank.Deprecated

    stmt_mainsnak = stmt_in["mainsnak"]
    stmt_property = stmt_mainsnak["property"]
    stmt_datatype = stmt_mainsnak["datatype"]
    if stmt_mainsnak["snaktype"] == 'novalue':
        stmt_value = False
    elif stmt_mainsnak["snaktype"] == 'somevalue':
        stmt_value = True
    else:
        stmt_value = tfsl.claim.build_value(stmt_mainsnak["datavalue"])
    stmt_quals = build_quals(stmt_in.get("qualifiers", None))
    stmt_refs = []
    if stmt_in.get("references", False):
        stmt_refs = [tfsl.reference.build_ref(ref) for ref in stmt_in["references"]]

    stmt_out = Statement(stmt_property, stmt_value, stmt_rank, stmt_quals, stmt_refs)
    stmt_out.set_published_settings(stmt_in)
    return stmt_out
