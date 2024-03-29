""" Intended to make certain commonly used derived types which depend only on tfsl itself easier to use.
    That this file imports no other (except for type checking purposes) is intentional.
"""

import re
from typing import Any, DefaultDict, Dict, List, NewType, Optional, Protocol, Sequence, Tuple, TypedDict, Union, TYPE_CHECKING, overload
from typing_extensions import NotRequired, TypeGuard

if TYPE_CHECKING:
    import tfsl.claim
    import tfsl.coordinatevalue
    import tfsl.item
    import tfsl.itemvalue
    import tfsl.languages
    import tfsl.lexeme
    import tfsl.lexemeform
    import tfsl.lexemesense
    import tfsl.monolingualtext
    import tfsl.quantityvalue
    import tfsl.statement
    import tfsl.timevalue

Qid_regex = re.compile(r"^Q[1-9]\d*$")
Pid_regex = re.compile(r"^P[1-9]\d*$")
Lid_regex = re.compile(r"^L[1-9]\d*$")
Fid_regex = re.compile(r"^F[1-9]\d*$")
Sid_regex = re.compile(r"^S[1-9]\d*$")
LFid_regex = re.compile(r"^(L[1-9]\d*)-(F[1-9]\d*)$")
LSid_regex = re.compile(r"^(L[1-9]\d*)-(S[1-9]\d*)$")

LanguageCode = NewType('LanguageCode', str)

Qid = NewType('Qid', str)
def is_Qid(arg: str) -> TypeGuard[Qid]: # pylint: disable=invalid-name
    """ Checks that a string is a Qid. """
    return Qid_regex.match(arg) is not None
def get_Qid_string(qid: Union[int, str]) -> Qid: # pylint: disable=invalid-name
    """ Extracts a Qid from a possible item reference. """
    if isinstance(qid, int):
        if qid > 0:
            return Qid('Q'+str(qid))
        raise ValueError('integer for Qid not greater than 0')
    elif is_Qid(qid):
        return qid
    raise ValueError('integer or Q string not provided')

Pid = NewType('Pid', str)
def is_Pid(arg: str) -> TypeGuard[Pid]: # pylint: disable=invalid-name
    """ Checks that a string is a Pid. """
    return Pid_regex.match(arg) is not None
def get_Pid_string(pid: Union[int, str]) -> Pid: # pylint: disable=invalid-name
    """ Extracts a Pid from a possible property reference. """
    if isinstance(pid, int):
        if pid > 0:
            return Pid('P'+str(pid))
        raise ValueError('integer for Pid not greater than 0')
    elif is_Pid(pid):
        return pid
    raise ValueError('integer or P string not provided')

Lid = NewType('Lid', str)
def is_Lid(arg: str) -> TypeGuard[Lid]: # pylint: disable=invalid-name
    """ Checks that a string is an Lid. """
    return Lid_regex.match(arg) is not None

Fid = NewType('Fid', str)
def is_Fid(arg: str) -> TypeGuard[Fid]: # pylint: disable=invalid-name
    """ Checks that a string is an Fid. """
    return Fid_regex.match(arg) is not None

Sid = NewType('Sid', str)
def is_Sid(arg: str) -> TypeGuard[Sid]: # pylint: disable=invalid-name
    """ Checks that a string is an Sid. """
    return Sid_regex.match(arg) is not None

LFid = NewType('LFid', str)
def is_LFid(arg: str) -> TypeGuard[LFid]: # pylint: disable=invalid-name
    """ Checks that a string is an LFid. """
    return LFid_regex.match(arg) is not None

def split_LFid(arg: LFid) -> Optional[Tuple[Lid, Fid]]: # pylint: disable=invalid-name
    """ Splits an LFid into the Lid part and the Fid part. """
    if matched_parts := LFid_regex.match(arg):
        lid_part: Optional[str] = matched_parts.group(1)
        fid_part: Optional[str] = matched_parts.group(2)
        if lid_part is not None and fid_part is not None:
            if is_Lid(lid_part) and is_Fid(fid_part):
                return lid_part, fid_part
    return None

LSid = NewType('LSid', str)
def is_LSid(arg: str) -> TypeGuard[LSid]: # pylint: disable=invalid-name
    """ Checks that a string is an LSid. """
    return LSid_regex.match(arg) is not None

def split_LSid(arg: LSid) -> Optional[Tuple[Lid, Sid]]: # pylint: disable=invalid-name
    """ Splits an LSid into the Lid part and the Sid part. """
    if matched_parts := LSid_regex.match(arg):
        lid_part: Optional[str] = matched_parts.group(1)
        sid_part: Optional[str] = matched_parts.group(2)
        if lid_part is not None and sid_part is not None:
            if is_Lid(lid_part) and is_Sid(sid_part):
                return lid_part, sid_part
    return None

PossibleLexemeReference = Union[int, Lid, LFid, LSid]

def get_Lid_string(ref: PossibleLexemeReference) -> Lid: # pylint: disable=invalid-name
    """ Extracts an Lid from a possible lexeme reference. """
    if isinstance(ref, int):
        if ref > 0:
            return Lid('L'+str(ref))
        raise ValueError('integer for Lid not greater than 0')
    elif is_LSid(ref):
        if split_lsid := split_LSid(ref):
            lid, _ = split_lsid
            return lid
    elif is_LFid(ref):
        if split_lfid := split_LFid(ref):
            lid, _ = split_lfid
            return lid
    elif is_Lid(ref):
        return ref
    raise ValueError('integer or L string not provided')

EntityId = Union[Qid, Pid, Lid, LFid, LSid]
def is_EntityId(arg: str) -> TypeGuard[EntityId]: # pylint: disable=invalid-name
    """ Checks that a string is an EntityId. """
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

LexemeSenseLikeList = Sequence['tfsl.lexemesense.LexemeSenseLike']
LexemeFormLikeList = Sequence['tfsl.lexemeform.LexemeFormLike']
LexemeLikeList = List['tfsl.lexeme.LexemeLike']

LexemeSenseList = List['tfsl.lexemesense.LexemeSense']
LexemeFormList = List['tfsl.lexemeform.LexemeForm']
LexemeList = List['tfsl.lexeme.Lexeme']

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
    'qualifiers-order': NotRequired[List[Pid]],
    'remove': NotRequired[str]
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

class PropertyPublishedSettings(EntityPublishedSettings, total=False):
    """ In the output of wikidata.org/wiki/Special:EntityData/P5578.json,
        those entries in the dictionary represented by the XPath "/entities/P5578"
        which are only relevant at editing time and not otherwise in EntityPublishedSettings.
    """
    id: NotRequired[Pid]
    type: NotRequired[str]

class PropertyDict(PropertyPublishedSettings, PropertyData):
    """ In the output of wikidata.org/wiki/Special:EntityData/P5578.json,
        the dictionary represented by the XPath "/entities/P5578".
    """

class ItemDict(ItemPublishedSettings, ItemData):
    """ In the output of wikidata.org/wiki/Special:EntityData/Q1356.json,
        the dictionary represented by the XPath "/entities/Q1356".
    """

class MTST(Protocol):
    """ A number of Wikibase entities contain as top-level subentities 1) a container of statements
        and 2) a container of monolingual text values. This Protocol exists to be used by other Protocols
        to allow accesses of these entities in similar ways.
    """
    def haswbstatement(self, property_in: Pid, value_in: Optional[ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""

    @overload
    def __getitem__(self, arg: 'tfsl.languages.Language') -> 'tfsl.monolingualtext.MonolingualText': ...
    @overload
    def __getitem__(self, arg: 'tfsl.monolingualtext.MonolingualText') -> 'tfsl.monolingualtext.MonolingualText': ...
    @overload
    def __getitem__(self, arg: Pid) -> StatementList: ...
    @overload
    def __getitem__(self, arg: 'tfsl.itemvalue.ItemValue') -> StatementList: ...

def is_EntityPublishedSettings(arg: Dict[str, Any]) -> TypeGuard[EntityPublishedSettings]: # pylint: disable=invalid-name
    """ Checks that the keys expected for a published entity exist. """
    return all(x in arg for x in ["pageid", "ns", "title", "lastrevid", "modified"])

def is_PropertyDict(arg: EntityPublishedSettings) -> TypeGuard[PropertyDict]: # pylint: disable=invalid-name
    """ Checks that the keys expected for a Property exist. """
    return all(x in arg for x in ["datatype", "labels", "descriptions", "aliases", "claims"])

def is_ItemDict(arg: EntityPublishedSettings) -> TypeGuard[ItemDict]: # pylint: disable=invalid-name
    """ Checks that the keys expected for an Item exist. """
    return all(x in arg for x in ["labels", "descriptions", "aliases", "claims", "sitelinks"])

def is_LexemeDict(arg: EntityPublishedSettings) -> TypeGuard[LexemeDict]: # pylint: disable=invalid-name
    """ Checks that the keys expected for an Item exist. """
    return all(x in arg for x in ["lemmas", "lexicalCategory", "language", "claims", "forms", "senses"])

Entity = Union[
    'tfsl.lexeme.Lexeme',
    'tfsl.lexemeform.LexemeForm',
    'tfsl.lexemesense.LexemeSense'
]
EntityLike = Union[
    'tfsl.lexemeform.LexemeFormLike',
    'tfsl.lexemesense.LexemeSenseLike'
]
EntityDict = Union[LexemeDict, LexemeFormDict, LexemeSenseDict]

StatementHolderInput = Union[StatementSet, StatementList]

MonolingualTextHolderInput = Union['tfsl.monolingualtext.MonolingualText', MonolingualTextList]

LanguageOrMT = Union['tfsl.languages.Language', 'tfsl.monolingualtext.MonolingualText']
