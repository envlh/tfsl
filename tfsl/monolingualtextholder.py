from copy import deepcopy

import tfsl.monolingualtext

class MonolingualTextHolder:
    def __init__(self, texts=None, **others):
        super().__init__()
        if isinstance(texts, tfsl.monolingualtext.MonolingualText):
            self.texts = [texts.text @ texts.language]
        elif isinstance(texts, list):
            self.texts = deepcopy(texts)
        else:
            self.texts = []

    def build_text_dict(self):
        return {text.language.code: {"value": text.text, "language": text.language.code} for text in self.texts}

    def __eq__(self, rhs):
        return self.texts == rhs.texts

def build_text_list(text_dict):
    texts = []
    for code, text in text_dict.items():
        new_text = text["value"] @ tfsl.languages.get_first_lang(text["language"])
        texts.append(new_text)
    return texts
