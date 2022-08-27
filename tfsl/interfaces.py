""" Intended to make certain commonly used derived types which depend only on tfsl itself easier to use.
    That this file imports no other (except for type checking purposes) is intentional.
"""

import re
from typing import Any, DefaultDict, Dict, List, NewType, Optional, Tuple, TypedDict, Union, TYPE_CHECKING
from typing_extensions import NotRequired, TypeGuard

if TYPE_CHECKING:
    import tfsl.claim
    import tfsl.coordinatevalue
    import tfsl.item
    import tfsl.itemvalue
    import tfsl.lexeme
    import tfsl.lexemeform
    import tfsl.lexemesense
    import tfsl.monolingualtext
    import tfsl.quantityvalue
    import tfsl.statement
    import tfsl.timevalue

Qid_regex = re.compile(r"^Q\d+$")
Pid_regex = re.compile(r"^P\d+$")
Lid_regex = re.compile(r"^L\d+$")
Fid_regex = re.compile(r"^F\d+$")
Sid_regex = re.compile(r"^S\d+$")
LFid_regex = re.compile(r"^(L\d+)-(F\d+)$")
LSid_regex = re.compile(r"^(L\d+)-(S\d+)$")

LanguageCode = NewType('LanguageCode', str)

Qid = NewType('Qid', str)
def is_Qid(arg: str) -> TypeGuard[Qid]:
    """ Checks that a string is a Qid. """
    return Qid_regex.match(arg) is not None
def isinstance_Qid(arg: Any) -> TypeGuard[Qid]:
    """ The above, but with an instance check beforehand.
        Use only when the arg is not guaranteed to be a str.
    """
    return isinstance(arg, str) and is_Qid(arg)

Pid = NewType('Pid', str)
def is_Pid(arg: str) -> TypeGuard[Pid]:
    """ Checks that a string is a Pid. """
    return Pid_regex.match(arg) is not None

Lid = NewType('Lid', str)
def is_Lid(arg: str) -> TypeGuard[Lid]:
    """ Checks that a string is an Lid. """
    return Lid_regex.match(arg) is not None

Fid = NewType('Fid', str)
def is_Fid(arg: str) -> TypeGuard[Fid]:
    """ Checks that a string is an Fid. """
    return Fid_regex.match(arg) is not None

Sid = NewType('Sid', str)
def is_Sid(arg: str) -> TypeGuard[Sid]:
    """ Checks that a string is an Sid. """
    return Sid_regex.match(arg) is not None

LFid = NewType('LFid', str)
def is_LFid(arg: str) -> TypeGuard[LFid]:
    """ Checks that a string is an LFid. """
    return LFid_regex.match(arg) is not None

def split_LFid(arg: LFid) -> Optional[Tuple[Lid, Fid]]:
    """ Splits an LFid into the Lid part and the Fid part. """
    if matched_parts := LFid_regex.match(arg):
        lid_part: Optional[str] = matched_parts.group(1)
        fid_part: Optional[str] = matched_parts.group(2)
        if lid_part is not None and fid_part is not None:
            if is_Lid(lid_part) and is_Fid(fid_part):
                return lid_part, fid_part
    return None

LSid = NewType('LSid', str)
def is_LSid(arg: str) -> TypeGuard[LSid]:
    """ Checks that a string is an LSid. """
    return LSid_regex.match(arg) is not None

def split_LSid(arg: LSid) -> Optional[Tuple[Lid, Sid]]:
    """ Splits an LSid into the Lid part and the Sid part. """
    if matched_parts := LSid_regex.match(arg):
        lid_part: Optional[str] = matched_parts.group(1)
        sid_part: Optional[str] = matched_parts.group(2)
        if lid_part is not None and sid_part is not None:
            if is_Lid(lid_part) and is_Sid(sid_part):
                return lid_part, sid_part
    return None

EntityId = Union[Qid, Pid, Lid, LFid, LSid]
def is_EntityId(arg: str) -> TypeGuard[EntityId]:
    return is_Qid(arg) or is_Lid(arg) or is_LSid(arg) or is_LFid(arg) or is_Pid(arg)

class MonolingualTextDict(TypedDict):
    """ Representation of the Wikibase 'monolingualtext' datatype. """
    text: str
    language: LanguageCode

class CoordinateValueDict(TypedDict):
    """ Representation of the Wikibase 'globecoordinate' datatype. """
    latitude: float
    longitude: float
    altitude: Optional[float]
    precision: float
    globe: str

class QuantityValueDict(TypedDict):
    """ Representation of the Wikibase 'quantity' datatype. """
    amount: float
    unit: str
    upperBound: NotRequired[float]
    lowerBound: NotRequired[float]

class TimeValueDict(TypedDict):
    """ Representation of the Wikibase 'time' datatype. """
    time: str
    timezone: int
    before: int
    after: int
    precision: int
    calendarmodel: str

ItemValueDict = TypedDict('ItemValueDict', {'entity-type': str, 'id': EntityId, 'numeric-id': NotRequired[int]})

ClaimDictValueDictionary = Union[CoordinateValueDict, MonolingualTextDict, ItemValueDict, QuantityValueDict, TimeValueDict]
ClaimDictValue = Union[str, ClaimDictValueDictionary]

class ClaimDictDatavalue(TypedDict):
    """ The actual value of a Claim or of a Statement. """
    value: ClaimDictValue
    type: str

class ClaimDict(TypedDict, total=False):
    """ A property-value pairing in places other than the main portion of a statement,
        such as a qualifier or a reference.
    """
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

ClaimList = List['tfsl.claim.Claim']
StatementList = List['tfsl.statement.Statement']
MonolingualTextList = List['tfsl.monolingualtext.MonolingualText']
LexemeSenseList = List['tfsl.lexemesense.LexemeSense']
LexemeFormList = List['tfsl.lexemeform.LexemeForm']
ReferenceList = List['tfsl.reference.Reference']

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
    """ Those entries in a StatementDict which pertain to informational content. """
    mainsnak: ClaimDict
    type: str
    qualifiers: NotRequired[ClaimDictSet]
    rank: str
    references: NotRequired[List[ReferenceDict]]

class StatementDict(StatementData, StatementDictPublishedSettings): # pylint: disable=inherit-non-class
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993.json,
        the dictionaries in the arrays represented by the XPath "/entities/L301993/claims/*".
    """

StatementDictSet = Dict[Pid, List[StatementDict]]

StatementSet = DefaultDict[Pid, List['tfsl.statement.Statement']]

class LemmaDict(TypedDict, total=False):
    """ Pairings of a language with a string value, such as, among others,
        in the output of wikidata.org/wiki/Special:EntityData/L301993.json,
        the dictionaries represented by the XPath "/entities/L301993/lemmas/*".
    """
    language: LanguageCode
    value: str
    remove: NotRequired[str]

LemmaDictSet = Dict[LanguageCode, LemmaDict]

class LexemeFormPublishedSettings(TypedDict, total=False):
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993-F1.json,
        those entries in the dictionary represented by the XPath "/entities/L301993-F1"
        which are only relevant at editing time and not otherwise in EntityPublishedSettings.
    """
    id: NotRequired[str]

class LexemeFormData(TypedDict, total=False):
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993-F1.json,
        those entries in the dictionary represented by the XPath "/entities/L301993-F1"
        which pertain to informational content.
    """
    representations: LemmaDictSet
    grammaticalFeatures: List[Qid]
    claims: StatementDictSet
    add: NotRequired[str]

class LexemeFormDict(LexemeFormPublishedSettings, LexemeFormData):
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993.json,
        the entries in the array represented by the XPath "/entities/L301993/forms".

        Alternatively, in the output of wikidata.org/wiki/Special:EntityData/L301993-F1.json,
        the dictionary represented by the XPath "/entities/L301993-F1".
    """

class LexemeSensePublishedSettings(TypedDict, total=False):
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993-S1.json,
        those entries in the dictionary represented by the XPath "/entities/L301993-S1"
        which are only relevant at editing time and not otherwise in EntityPublishedSettings.
    """
    id: NotRequired[str]

class LexemeSenseData(TypedDict, total=False):
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993-S1.json,
        those entries in the dictionary represented by the XPath "/entities/L301993-S1"
        which pertain to informational content.
    """
    glosses: LemmaDictSet
    claims: StatementDictSet
    add: NotRequired[str]

class LexemeSenseDict(LexemeSensePublishedSettings, LexemeSenseData):
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993.json,
        the entries in the array represented by the XPath "/entities/L301993/senses".

        Alternatively, in the output of wikidata.org/wiki/Special:EntityData/L301993-S1.json,
        the dictionary represented by the XPath "/entities/L301993-S1".
    """

class EntityPublishedSettings(TypedDict, total=False):
    """ In the output of wikidata.org/wiki/Special:EntityData/Q1356.json,
        those entries in the dictionary represented by the XPath "/entities/Q1356"
        which are only relevant at editing time
        and are common to all entities returned by Special:EntityData.
    """
    pageid: NotRequired[int]
    ns: NotRequired[int]
    title: NotRequired[str]
    lastrevid: NotRequired[int]
    modified: NotRequired[str]

class LexemeData(TypedDict):
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993.json,
        those entries in the dictionary represented by the XPath "/entities/L301993"
        which pertain to informational content.
    """
    lexicalCategory: Qid
    language: Qid
    lemmas: LemmaDictSet
    claims: StatementDictSet
    forms: List[LexemeFormDict]
    senses: List[LexemeSenseDict]

class LexemePublishedSettings(EntityPublishedSettings, total=False):
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993.json,
        those entries in the dictionary represented by the XPath "/entities/L301993"
        which are only relevant at editing time and not otherwise in EntityPublishedSettings.
    """
    id: NotRequired[Lid]
    type: NotRequired[str]

class LexemeDict(LexemePublishedSettings, LexemeData):
    """ In the output of wikidata.org/wiki/Special:EntityData/L301993.json,
        the dictionary represented by the XPath "/entities/L301993".
    """

class SitelinkDict(TypedDict):
    """ In the output of wikidata.org/wiki/Special:EntityData/Q1356.json,
        the dictionaries represented by the XPath "/entities/Q1356/sitelinks/*".
    """
    site: str
    title: str
    badges: List[Qid]
    url: str

class PropertyData(TypedDict):
    """ In the output of wikidata.org/wiki/Special:EntityData/P5578.json,
        those entries in the dictionary represented by the XPath "/entities/P5578"
        which pertain to informational content.
    """
    datatype: str
    labels: LemmaDictSet
    descriptions: LemmaDictSet
    aliases: Dict[LanguageCode, List[LemmaDict]]
    claims: StatementDictSet

class ItemData(TypedDict):
    """ In the output of wikidata.org/wiki/Special:EntityData/Q1356.json,
        those entries in the dictionary represented by the XPath "/entities/Q1356"
        which pertain to informational content.
    """
    labels: LemmaDictSet
    descriptions: LemmaDictSet
    aliases: Dict[LanguageCode, List[LemmaDict]]
    claims: StatementDictSet
    sitelinks: Dict[str, SitelinkDict]

class ItemPublishedSettings(EntityPublishedSettings, total=False):
    """ In the output of wikidata.org/wiki/Special:EntityData/Q1356.json,
        those entries in the dictionary represented by the XPath "/entities/Q1356"
        which are only relevant at editing time and not otherwise in EntityPublishedSettings.
    """
    id: NotRequired[Qid]
    type: NotRequired[str]

class PropertyDict(ItemPublishedSettings, PropertyData):
    """ In the output of wikidata.org/wiki/Special:EntityData/P5578.json,
        the dictionary represented by the XPath "/entities/P5578".
    """

class ItemDict(ItemPublishedSettings, ItemData):
    """ In the output of wikidata.org/wiki/Special:EntityData/Q1356.json,
        the dictionary represented by the XPath "/entities/Q1356".
    """

def is_ItemDict(arg: EntityPublishedSettings) -> TypeGuard[ItemDict]:
    """ Checks that the keys expected for an Item exist. """
    return all(x in arg for x in ["labels", "descriptions", "aliases", "claims", "sitelinks"])

Entity = Union[
    'tfsl.lexeme.Lexeme',
    'tfsl.lexemeform.LexemeForm',
    'tfsl.lexemesense.LexemeSense'
]
EntityDict = Union[LexemeDict, LexemeFormDict, LexemeSenseDict]

StatementHolderInput = Union[StatementSet, StatementList]

MonolingualTextHolderInput = Union['tfsl.monolingualtext.MonolingualText', MonolingualTextList]

LanguageOrMT = Union['tfsl.languages.Language', 'tfsl.monolingualtext.MonolingualText']
