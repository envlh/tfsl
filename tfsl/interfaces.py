""" Intended to make certain commonly used derived types which depend only on tfsl itself easier to use.
    That this file imports no other (except for type checking purposes) is intentional.
"""

import re
from typing import DefaultDict, Dict, List, NewType, Optional, Tuple, TypedDict, Union, TYPE_CHECKING
from typing_extensions import NotRequired, TypeGuard

if TYPE_CHECKING:
    import tfsl.claim
    import tfsl.coordinatevalue
    import tfsl.itemvalue
    import tfsl.monolingualtext
    import tfsl.quantityvalue
    import tfsl.statement
    import tfsl.timevalue

EntityId = NewType('EntityId', str)

LanguageCode = NewType('LanguageCode', str)
Qid = NewType('Qid', EntityId)
def is_Qid(arg: str) -> TypeGuard[Qid]:
    return re.match(r"^Q\d+$", arg) is not None

Pid = NewType('Pid', EntityId)
def is_Pid(arg: str) -> TypeGuard[Pid]:
    return re.match(r"^P\d+$", arg) is not None

Lid = NewType('Lid', EntityId)
def is_Lid(arg: str) -> TypeGuard[Lid]:
    return re.match(r"^L\d+$", arg) is not None

Fid = NewType('Fid', str)
def is_Fid(arg: str) -> TypeGuard[Fid]:
    return re.match(r"^F\d+$", arg) is not None

Sid = NewType('Sid', str)
def is_Sid(arg: str) -> TypeGuard[Sid]:
    return re.match(r"^S\d+$", arg) is not None

LFid = NewType('LFid', str)
def is_LFid(arg: str) -> TypeGuard[LFid]:
    return re.match(r"^(L\d+)-(F\d+)$", arg) is not None

def split_LFid(arg: LFid) -> Optional[Tuple[Lid, Fid]]:
    if matched_parts := re.match(r"^(L\d+)-(F\d+)$", arg):
        lid_part: Optional[str] = matched_parts.group(1)
        fid_part: Optional[str] = matched_parts.group(2)
        if lid_part is not None and fid_part is not None:
            if is_Lid(lid_part) and is_Fid(fid_part):
                return lid_part, fid_part
    return None

LSid = NewType('LSid', str)
def is_LSid(arg: str) -> TypeGuard[LSid]:
    return re.match(r"^(L\d+)-(S\d+)$", arg) is not None

def split_LSid(arg: LSid) -> Optional[Tuple[Lid, Sid]]:
    if matched_parts := re.match(r"^(L\d+)-(S\d+)$", arg):
        lid_part: Optional[str] = matched_parts.group(1)
        sid_part: Optional[str] = matched_parts.group(2)
        if lid_part is not None and sid_part is not None:
            if is_Lid(lid_part) and is_Sid(sid_part):
                return lid_part, sid_part
    return None

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

StatementDictPublishedSettings = TypedDict('StatementDictPublishedSettings', {
    'id': NotRequired[str],
    'qualifiers-order': NotRequired[List[Pid]]
}, total=False)

class StatementData(TypedDict, total=False):
    mainsnak: ClaimDict
    type: str
    qualifiers: NotRequired[ClaimDictSet]
    rank: str
    references: NotRequired[List[ReferenceDict]]

class StatementDict(StatementData, StatementDictPublishedSettings): # pylint: disable=inherit-non-class
    pass

StatementDictSet = Dict[Pid, List[StatementDict]]

StatementSet = DefaultDict[Pid, List['tfsl.statement.Statement']]

class LemmaDict(TypedDict, total=False):
    language: LanguageCode
    value: str
    remove: NotRequired[str]

LemmaDictSet = Dict[LanguageCode, LemmaDict]

class LexemeFormPublishedSettings(TypedDict, total=False):
    id: NotRequired[str]

class LexemeFormData(TypedDict, total=False):
    representations: LemmaDictSet
    grammaticalFeatures: List[Qid]
    claims: StatementDictSet
    add: NotRequired[str]

class LexemeFormDict(LexemeFormPublishedSettings, LexemeFormData):
    pass

class LexemeSensePublishedSettings(TypedDict, total=False):
    id: NotRequired[str]

class LexemeSenseData(TypedDict, total=False):
    glosses: LemmaDictSet
    claims: StatementDictSet
    add: NotRequired[str]

class LexemeSenseDict(LexemeSensePublishedSettings, LexemeSenseData):
    pass

class EntityPublishedSettings(TypedDict, total=False):
    pageid: NotRequired[int]
    ns: NotRequired[int]
    title: NotRequired[str]
    lastrevid: NotRequired[int]
    modified: NotRequired[str]
    id: NotRequired[str]

class LexemeData(TypedDict):
    lexicalCategory: Qid
    language: Qid
    lemmas: LemmaDictSet
    claims: StatementDictSet
    forms: List[LexemeFormDict]
    senses: List[LexemeSenseDict]

class LexemePublishedSettings(EntityPublishedSettings, total=False):
    type: NotRequired[str]

class LexemeDict(LexemePublishedSettings, LexemeData):
    pass

class SitelinkDict(TypedDict):
    site: str
    title: str
    badges: List[Qid]
    url: str

class ItemData(TypedDict):
    labels: LemmaDictSet
    descriptions: LemmaDictSet
    aliases: Dict[LanguageCode, List[LemmaDict]]
    claims: StatementDictSet
    sitelinks: Dict[str, SitelinkDict]

class ItemPublishedSettings(EntityPublishedSettings, total=False):
    type: NotRequired[str]

class ItemDict(ItemPublishedSettings, ItemData):
    pass

def is_ItemDict(arg: EntityPublishedSettings) -> TypeGuard[ItemDict]:
    return all(x in arg for x in ["labels", "descriptions", "aliases", "claims", "sitelinks"])
