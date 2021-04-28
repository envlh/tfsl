from functools import singledispatchmethod
import json

import tfsl.languages

class MonolingualText:
    """ Representation of a value to which a language is tied.
        As far as claims go, this is usable directly as a monolingual text value;
        it can, however, be used to specify a language with accompanying text,
        such as is useful to determine terms in a termbox or lexeme representations.
    """
    def __init__(self, text: str, language: 'tfsl.languages.Language'):
        self.text = text
        self.language = language

    # TODO: should I compare against strings?
    def __eq__(self, rhs):
        return self.text == rhs.text and self.language == rhs.language

    def __hash__(self):
        return hash((self.text, self.language))
        
    def __str__(self):
        return f'{self.text}@{self.language.code} ({self.language.item})'

    def __jsonout__(self):
        return {
                   "text": self.text,
                   "language": self.language.code
               }

def build_mtvalue(value_in):
    return MonolingualText(value_in["text"], tfsl.languages.langs.find(value_in["language"])[0])
