from collections import defaultdict, Counter
from copy import deepcopy
from functools import singledispatchmethod
from textwrap import indent
from typing import Any, Tuple

import tfsl.claim
import tfsl.utils


class Reference:
    """ Representation of a reference.
    """
    # TODO: define __setitem__

    def __init__(self, *args):
        self._claims = defaultdict(list)
        if(len(args) == 1 and type(args[0]) == defaultdict):
            self._claims = deepcopy(args[0])
        else:
            if(len(args) == 1 and type(args[0]) == list):
                arglist = args[0]
            else:
                arglist = args
            for arg in arglist:
                self._claims[arg.property].append(deepcopy(arg))

    def __getitem__(self, property_in: str):
        return self._claims[property_in]

    def __delitem__(self, claim_in):
        if(type(claim_in) == str):
            del self._claims[claim_in]
        else:
            self._claims[claim_in[0]] = [claim for claim in self._claims[claim_in[0]] if claim.value != claim_in[1]]

    def __add__(self, arg):
        newclaims = self.add(arg)
        return Reference(newclaims)

    @singledispatchmethod
    def add(self, arg):
        if isinstance(arg, tfsl.claim.Claim):
            return tfsl.utils.add_claimlike(self._claims, arg)
        return self._claims

    def __sub__(self, arg):
        newclaims = self.sub(arg)
        return Reference(newclaims)

    @singledispatchmethod
    def sub(self, arg):
        if isinstance(arg, tfsl.claim.Claim):
            return tfsl.utils.sub_claimlike(self._claims, arg)
        return self._claims

    def __contains__(self, arg):
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg):
        if isinstance(arg, tfsl.claim.Claim):
            for prop in self._claims:
                if arg in self._claims[prop]:
                    return True
        return arg in self._claims[arg.property]

    @contains.register
    def _(self, arg: str):
        return arg in self._claims

    def __eq__(self, rhs):
        return Counter(self._claims) == Counter(rhs._claims)

    def __hash__(self):
        return hash((claim for k, v in self._claims.items() for claim in v))

    def __str__(self):
        return "["+indent("\n".join([str(claim) for key in self._claims for claim in self._claims[key]]), tfsl.utils.DEFAULT_INDENT)+"]"

    def __jsonout__(self):
        snaks_order = list(self._claims.keys())
        base_dict = {
                        "snaks-order": snaks_order
                    }
        base_dict["snaks"] = defaultdict(list)
        for snak in snaks_order:
            for claim in self._claims[snak]:
                base_dict["snaks"][snak].append(claim.__jsonout__())
        base_dict["snaks"] = dict(base_dict["snaks"])
        try:
            base_dict["hash"] = self.hash
        except AttributeError:
            pass
        return base_dict


def build_ref(ref_in):
    claim_list = ref_in["snaks"]
    ref_claims = defaultdict(list)
    for prop in claim_list:
        for claim in claim_list[prop]:
            ref_claims[prop].append(tfsl.claim.build_claim(claim))

    ref_out = Reference(ref_claims)
    ref_out.snaks_order = ref_in["snaks-order"]
    ref_out.hash = ref_in["hash"]
    return ref_out
