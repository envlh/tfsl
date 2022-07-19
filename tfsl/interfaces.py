""" Intended to make certain commonly used derived types which depend only on tfsl itself easier to use.
    That this file imports no other (except for type checking purposes) is intentional.
"""

import re
from typing import Dict, List, Literal, NewType, Optional, TypedDict, Union, TYPE_CHECKING
from typing_extensions import NotRequired, TypeGuard

if TYPE_CHECKING:
    import tfsl.claim
    import tfsl.coordinatevalue
    import tfsl.itemvalue
    import tfsl.monolingualtext
    import tfsl.quantityvalue
    import tfsl.statement
    import tfsl.timevalue

LanguageCode = NewType('LanguageCode', str)
Qid = NewType('Qid', str)
def is_Qid(arg: str) -> TypeGuard[Qid]:
    return re.match(r"^Q\d+$", arg) is not None

Pid = NewType('Pid', str)
def is_Pid(arg: str) -> TypeGuard[Pid]:
    return re.match(r"^P\d+$", arg) is not None

Lid = NewType('Lid', str)
def is_Lid(arg: str) -> TypeGuard[Lid]:
    return re.match(r"^L\d+$", arg) is not None

class MonolingualTextDict(TypedDict):
    text: str
    language: LanguageCode

class CoordinateValueDict(TypedDict):
    latitude: float
    longitude: float
    altitude: Optional[float]
    precision: float
    globe: str

class QuantityValueDict(TypedDict, total=False):
    amount: float
    unit: str
    upperBound: NotRequired[float]
    lowerBound: NotRequired[float]

class TimeValueDict(TypedDict):
    time: str
    timezone: int
    before: int
    after: int
    precision: int
    calendarmodel: str

ItemValueDict = TypedDict('ItemValueDict', {'entity-type': str, 'id': str, 'numeric-id': NotRequired[int]}, total=False)

ClaimDictValueDictionary = Union[CoordinateValueDict, MonolingualTextDict, ItemValueDict, QuantityValueDict, TimeValueDict]
ClaimDictValue = Union[str, ClaimDictValueDictionary]

class ClaimDictDatavalue(TypedDict):
    value: ClaimDictValue
    type: str

class ClaimDict(TypedDict, total=False):
    property: Pid
    snaktype: str
    hash: str
    datavalue: ClaimDictDatavalue
    datatype: str

ClaimValue = Union[
    bool,
    'tfsl.coordinatevalue.CoordinateValue',
    'tfsl.itemvalue.ItemValue',
    'tfsl.monolingualtext.MonolingualText',
    'tfsl.quantityvalue.QuantityValue',
    str,
    'tfsl.timevalue.TimeValue'
]

ClaimDictSet = Dict[Pid, List[ClaimDict]]

ClaimSet = Dict[Pid, List['tfsl.claim.Claim']]

ReferenceDict = TypedDict('ReferenceDict', {
    'snaks-order': List[Pid],
    'snaks': ClaimDictSet,
    'hash': NotRequired[str]
}, total=False)

StatementDict = TypedDict('StatementDict', {
    'mainsnak': ClaimDict,
    'type': str,
    'id': NotRequired[str],
    'qualifiers': NotRequired[ClaimDictSet],
    'qualifiers-order': NotRequired[List[Pid]],
    'rank': str,
    'references': NotRequired[List[ReferenceDict]]
}, total=False)

StatementDictSet = Dict[Pid, List[StatementDict]]

StatementSet = Dict[Pid, List['tfsl.statement.Statement']]

class LemmaDict(TypedDict, total=False):
    language: LanguageCode
    value: str
    remove: NotRequired[str]

LemmaDictSet = Dict[LanguageCode, LemmaDict]

class LexemeFormDict(TypedDict):
    id: Optional[str]
    representations: LemmaDictSet
    grammaticalFeatures: List[Qid]
    claims: ClaimDictSet

class LexemeSenseDict(TypedDict):
    id: Optional[str]
    glosses: LemmaDictSet
    claims: ClaimDictSet

class LexemeDict(TypedDict):
    pageid: Optional[int]
    ns: Optional[int]
    title: Optional[str]
    lastrevid: Optional[int]
    modified: Optional[str]
    type: Optional[str]
    id: Optional[str]
    lemmas: LemmaDictSet
    claims: ClaimDictSet
    forms: List[LexemeFormDict]
    senses: List[LexemeSenseDict]
