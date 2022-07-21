""" Holds the MonolingualText class and a function to build one given a JSON representation of it. """

from typing_extensions import TypeGuard

import tfsl.interfaces as I
import tfsl.languages

class MonolingualText:
    """ Representation of a value to which a language is tied.
        As far as claims go, this is usable directly as a monolingual text value;
        it can, however, be used to specify a language with accompanying text,
        such as is useful to determine terms in a termbox or lexeme representations.
    """
    def __init__(self, text: str, language: 'tfsl.languages.Language'):
        self.text: str = text
        self.language: 'tfsl.languages.Language' = language

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, MonolingualText):
            return NotImplemented
        return self.text == rhs.text and self.language == rhs.language

    def __hash__(self) -> int:
        return hash((self.text, self.language))

    def __str__(self) -> str:
        return f'{self.text}@{self.language.code} ({self.language.item})'

    def __repr__(self) -> str:
        return f'{self.text}@{self.language.code} ({self.language.item})'

    def __jsonout__(self) -> I.MonolingualTextDict:
        return {
            "text": self.text,
            "language": self.language.code
        }

def is_mtvalue(value_in: I.ClaimDictValueDictionary) -> TypeGuard[I.MonolingualTextDict]:
    """ Checks that the keys expected for a MonolingualText exist. """
    return all(key in value_in for key in ["text", "language"])

def build_mtvalue(value_in: I.MonolingualTextDict) -> MonolingualText:
    """ Builds a MonolingualText given the Wikibase JSON for one. """
    return MonolingualText(value_in["text"], tfsl.languages.get_first_lang(value_in["language"]))
