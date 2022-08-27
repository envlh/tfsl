""" Holds the StatementHolder class and a function to build one given a JSON representation of it. """

from copy import deepcopy
from functools import singledispatchmethod
from typing import Callable, Optional, Union

import tfsl.interfaces as I
import tfsl.languages
import tfsl.monolingualtext

def rep_language_is(desired_language: tfsl.languages.Language) -> Callable[[tfsl.monolingualtext.MonolingualText], bool]:
    """ Returns a function checking that the provided MonolingualText is in a certain language. """
    def is_desired_language(text: tfsl.monolingualtext.MonolingualText) -> bool:
        return text.language == desired_language
    return is_desired_language

class MonolingualTextHolder(object):
    """ Holds a set of strings with languages attached to them. """
    def __init__(self,
                 texts: Optional[I.MonolingualTextHolderInput]=None,
                 removed_texts: Optional[I.MonolingualTextList]=None):
        super().__init__()

        self.texts: I.MonolingualTextList
        if isinstance(texts, tfsl.monolingualtext.MonolingualText):
            self.texts = [texts.text @ texts.language]
        elif texts is None:
            self.texts = []
        else:
            self.texts = texts

        if removed_texts is None:
            self.removed_texts: I.MonolingualTextList = []
        else:
            self.removed_texts = removed_texts

    def __jsonout__(self) -> I.LemmaDictSet:
        base_dict: I.LemmaDictSet = {text.language.code: {"value": text.text, "language": text.language.code, "remove": ""} for text in self.removed_texts}
        for text in self.texts:
            base_dict[text.language.code] = {"value": text.text, "language": text.language.code}
        return base_dict

    def __eq__(self, rhs: object) -> bool:
        if isinstance(rhs, MonolingualTextHolder):
            return self.texts == rhs.texts
        elif isinstance(rhs, list):
            return set(self.texts) == set(rhs)
        return NotImplemented

    def __contains__(self, arg: object) -> bool:
        return self.contains(arg)

    def __len__(self) -> int:
        return len(self.texts)

    @singledispatchmethod
    def contains(self, arg: object) -> bool:
        """ Dispatches __contains__. """
        raise TypeError(f"Can't check for {type(arg)} in MonolingualTextHolder")

    @contains.register
    def _(self, arg: tfsl.languages.Language) -> bool:
        return any((text.language == arg) for text in self.texts)

    @contains.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText) -> bool:
        return arg in self.texts

    def __getitem__(self, arg: object) -> tfsl.monolingualtext.MonolingualText:
        return self.get_mt(arg)

    @singledispatchmethod
    def get_mt(self, arg: object) -> tfsl.monolingualtext.MonolingualText:
        """ Dispatches __getitem__. """
        raise TypeError(f"Can't get {type(arg)} from MonolingualTextHolder")

    @get_mt.register
    def _(self, arg: tfsl.languages.Language) -> tfsl.monolingualtext.MonolingualText:
        return next(filter(rep_language_is(arg), self.texts))

    @get_mt.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText) -> tfsl.monolingualtext.MonolingualText:
        return next(filter(lambda text: text == arg, self.texts))

    def __str__(self) -> str:
        return ' / '.join([str(text) for text in self.texts])

    def __add__(self, rhs: object) -> 'MonolingualTextHolder':
        if isinstance(rhs, tfsl.monolingualtext.MonolingualText):
            newtexts = deepcopy(self.texts)
            newtexts = [rep for rep in newtexts if rep.language != rhs.language]
            newtexts.append(rhs)
            return MonolingualTextHolder(newtexts)
        raise TypeError(f"Can't add {type(rhs)} to MonolingualTextHolder")

    def __sub__(self, rhs: object) -> 'MonolingualTextHolder':
        if isinstance(rhs, tfsl.languages.Language):
            newtexts = []
            for rep in self.texts:
                if rep.language == rhs:
                    self.removed_texts.append(rep)
                else:
                    newtexts.append(rep)
            return MonolingualTextHolder(newtexts)
        elif isinstance(rhs, tfsl.monolingualtext.MonolingualText):
            newtexts = [rep for rep in self.texts if rep != rhs]
            if rhs in self.texts:
                self.removed_texts.append(rhs)
            return MonolingualTextHolder(newtexts)
        raise TypeError(f"Can't subtract {type(rhs)} from MonolingualTextHolder")

def build_text_list(text_dict: I.LemmaDictSet) -> I.MonolingualTextList:
    """ Builds a statement set from a JSON dictionary of statements. """
    texts: I.MonolingualTextList = []
    for _, text in text_dict.items():
        new_text = text["value"] @ tfsl.languages.get_first_lang(text["language"])
        texts.append(new_text)
    return texts
