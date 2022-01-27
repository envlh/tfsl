from copy import deepcopy
from functools import singledispatchmethod
from typing import Union

import tfsl.monolingualtext

lang_or_mt = Union[tfsl.languages.Language, tfsl.monolingualtext.MonolingualText]

def rep_language_is(desired_language: tfsl.languages.Language):
    def is_desired_language(text: tfsl.monolingualtext.MonolingualText):
        return text.language == desired_language
    return is_desired_language

class MonolingualTextHolder:
    def __init__(self, **others):
        super().__init__()

        texts = others.get("texts", None)
        if isinstance(texts, tfsl.monolingualtext.MonolingualText):
            self.texts = [texts.text @ texts.language]
        elif isinstance(texts, list):
            self.texts = deepcopy(texts)
        else:
            self.texts = []
        self.removed_texts = []

    def build_text_dict(self):
        base_dict = {text.language.code: {"value": text.text, "language": text.language.code, "remove": ""} for text in self.removed_texts}
        for text in self.texts:
            base_dict[text.language.code] = {"value": text.text, "language": text.language.code}
        return base_dict

    def __eq__(self, rhs):
        return self.texts == rhs.texts

    def __contains__(self, arg):
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg):
        raise TypeError(f"Can't check for {type(arg)} in MonolingualTextHolder")

    @contains.register
    def _(self, arg: tfsl.languages.Language):
        return any((text.language == arg) for text in self.texts)

    @contains.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return arg in self.texts

    def __getitem__(self, arg):
        return self.get_mt(arg)

    @singledispatchmethod
    def get_mt(self, arg):
        raise TypeError(f"Can't get {type(arg)} from MonolingualTextHolder")

    @get_mt.register
    def _(self, arg: tfsl.languages.Language):
        return next(filter(rep_language_is(arg), self.texts))

    @get_mt.register
    def _(self, arg: tfsl.monolingualtext.MonolingualText):
        return next(filter(lambda text: text == arg, self.texts))

    def __str__(self):
        return ' / '.join([str(text) for text in self.texts])

def build_text_list(text_dict):
    texts = []
    for _, text in text_dict.items():
        new_text = text["value"] @ tfsl.languages.get_first_lang(text["language"])
        texts.append(new_text)
    return texts
