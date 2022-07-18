from collections import defaultdict, Counter
from copy import deepcopy
from functools import singledispatchmethod
from textwrap import indent
from typing import DefaultDict, ItemsView, List, Mapping, Optional, Union

import tfsl.interfaces as I
import tfsl.claim
import tfsl.utils

class ClaimSet(DefaultDict[I.Pid, List[tfsl.claim.Claim]]):
    def add(self, arg: tfsl.claim.Claim) -> 'ClaimSet':
        newclaimset = deepcopy(self)
        newclaimset[arg.property].append(arg)
        return newclaimset

    def sub(self, arg: tfsl.claim.Claim) -> 'ClaimSet':
        newclaimset = deepcopy(self)
        newclaimset[arg.property] = [claim for claim in newclaimset[arg.property] if claim != arg]
        if len(newclaimset[arg.property]) == 0:
            del newclaimset[arg.property]
        return newclaimset

class Reference:
    """ Representation of a reference. """
    # TODO: define __setitem__

    def __init__(self, *args: Union[tfsl.claim.Claim, ClaimSet]):
        self._claims = ClaimSet()
        for arg in args:
            if isinstance(arg, tfsl.claim.Claim):
                self._claims = self._claims.add(arg)
            else:
                for prop in arg:
                    for claim in arg[prop]:
                        self._claims = self._claims.add(claim)

        self.snaks_order: Optional[List[I.Pid]] = None
        self.hash: Optional[str] = None

    def __getitem__(self, property_in: I.Pid) -> List[tfsl.claim.Claim]:
        return self._claims[property_in]

    def __delitem__(self, arg: Union[I.Pid, tfsl.claim.Claim]) -> None:
        if isinstance(arg, tfsl.claim.Claim):
            self._claims[arg.property] = [claim for claim in self._claims[arg.property] if claim.value != arg.value]
        else:
            del self._claims[arg]

    def __add__(self, arg: object) -> 'Reference':
        newclaims = self.add(arg)
        return Reference(newclaims)

    @singledispatchmethod
    def add(self, arg: object) -> ClaimSet:
        raise ValueError(f"Cannot add {type(arg)} to Reference")

    @add.register
    def _(self, arg: tfsl.claim.Claim) -> ClaimSet:
        return self._claims.add(arg)

    def __sub__(self, arg: object) -> 'Reference':
        newclaims = self.sub(arg)
        return Reference(newclaims)

    @singledispatchmethod
    def sub(self, arg: object) -> ClaimSet:
        raise ValueError(f"Cannot subtract {type(arg)} from Reference")

    @sub.register
    def _(self, arg: tfsl.claim.Claim) -> ClaimSet:
        return self._claims.sub(arg)

    def __contains__(self, arg: object) -> bool:
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg: object) -> bool:
        return False

    @contains.register
    def _(self, arg: tfsl.claim.Claim) -> bool:
        return arg in self._claims[arg.property]

    @contains.register
    def _(self, arg: str) -> bool:
        return arg in self._claims

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, Reference):
            return NotImplemented
        return Counter(self._claims) == Counter(rhs._claims)

    def __hash__(self) -> int:
        return hash((claim for k, v in self._claims.items() for claim in v))

    def __str__(self) -> str:
        return "["+indent("\n".join([str(claim) for key in self._claims for claim in self._claims[key]]), tfsl.utils.DEFAULT_INDENT)+"]"

    def __jsonout__(self) -> I.ReferenceDict:
        snaks_order = list(self._claims.keys())
        base_dict: I.ReferenceDict = {
            "snaks-order": snaks_order
        }
        snak_dict = defaultdict(list)
        for snak in snaks_order:
            for claim in self._claims[snak]:
                snak_dict[snak].append(claim.__jsonout__())
        base_dict["snaks"] = dict(snak_dict)
        if self.hash is not None:
            base_dict["hash"] = self.hash
        return base_dict


def build_ref(ref_in: I.ReferenceDict) -> Reference:
    claim_dict: I.ClaimDictSet = ref_in["snaks"]
    ref_claims: List[tfsl.claim.Claim] = []
    for prop in claim_dict:
        for claim in claim_dict[prop]:
            ref_claims.append(tfsl.claim.build_claim(claim))

    ref_out = Reference(*ref_claims)
    ref_out.snaks_order = ref_in["snaks-order"]
    ref_out.hash = ref_in["hash"]
    return ref_out
