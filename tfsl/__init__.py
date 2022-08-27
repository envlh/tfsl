""" twofivesixlex -- a library to use and edit Wikidata items and lexemes """

# pylint: disable=useless-import-alias

from tfsl.auth import WikibaseSession as WikibaseSession
from tfsl.claim import Claim as Claim
from tfsl.coordinatevalue import CoordinateValue as CoordinateValue
from tfsl.item import Item as Item, Q as Q, Q_ as Q_
from tfsl.itemvalue import ItemValue as ItemValue
from tfsl.languages import Language as Language, langs as langs
from tfsl.lexeme import Lexeme as Lexeme, L as L
from tfsl.lexemeform import LexemeForm as LexemeForm
from tfsl.lexemesense import LexemeSense as LexemeSense
from tfsl.monolingualtext import MonolingualText as MonolingualText
from tfsl.monolingualtextholder import MonolingualTextHolder as MonolingualTextHolder
from tfsl.quantityvalue import QuantityValue as QuantityValue
from tfsl.reference import Reference as Reference
from tfsl.statement import Statement as Statement
from tfsl.statementholder import StatementHolder as StatementHolder
from tfsl.timevalue import TimeValue as TimeValue
import tfsl.interfaces as interfaces
import tfsl.utils as utils
