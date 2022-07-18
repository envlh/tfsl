""" Intended to make certain commonly used derived types which depend only on tfsl itself easier to use.
    That this file imports no other (except for type checking purposes) is intentional.
"""

from typing import Dict, List, Literal, NewType, Optional, TypedDict, Union, TYPE_CHECKING
from typing_extensions import NotRequired

if TYPE_CHECKING:
    import tfsl.coordinatevalue
    import tfsl.itemvalue
    import tfsl.monolingualtext
    import tfsl.quantityvalue
    import tfsl.timevalue

LanguageCode = NewType('LanguageCode', str)
Qid = NewType('Qid', str)
Pid = NewType('Pid', str)
Lid = NewType('Lid', str)

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