from functools import singledispatchmethod

import tfsl.monolingualtext

class Language:
    """ Container for languages.
        Note that due to their use literally anywhere a language is expected,
        the item should remain a string.
    """
    def __init__(self, code: str, item: str):
        self.code = code
        self.item = item

    def __str__(self):
        return f'{self.code} ({self.item})'
    
    def __eq__(self, rhs):
        return self.compare_eq(rhs)
    
    def __rmatmul__(self, text):
        return self.rmatmul(text)

    @singledispatchmethod
    def rmatmul(self, text):
        text.language = self
        return text
    
    @rmatmul.register
    def _(self, text: str):
        return tfsl.monolingualtext.MonolingualText(text, self)

    @rmatmul.register
    def _(self, text: tfsl.monolingualtext.MonolingualText):
        return tfsl.monolingualtext.MonolingualText(text.text, self)

    @singledispatchmethod
    def compare_eq(self, rhs):
        return self.item == rhs.item and self.code == rhs.code
    
    @compare_eq.register
    def _(self, rhs: str):
        if(rhs[0] == "Q"):
            return self.item == rhs
        return self.code == rhs
    
    def __hash__(self):
        return hash((self.code, self.item))

class langs():
    """ Mapping of BCP47 codes used on Wikimedia projects to Language objects.
        Only those whose codes are available either as termbox codes, monolingual text codes,
        or separate lexeme language codes should have entries here.
        (Dashes, if present in a code, should be substituted with underscores here.)
    """
    # TODO: find a way to convert from Qids to Language items
    
    # Eastern Indo-Aryan languages
    bn_ = Language("bn", "Q9610") # Bengali
    ctg_ = Language("ctg", "Q33173") # Chittagonian
    rkt_ = Language("rkt", "Q3241618") # Rangpuri
    syl_ = Language("syl", "Q2044560") # Sylheti
    ccp_ = Language("ccp", "Q32952") # Chakma
    rhg_rohg_ = Language("rhg-rohg", "Q3241177") # Rohingya
    as_ = Language("as", "Q29401") # Assamese
    or_ = Language("or", "Q33810") # Odia
    bho_ = Language("bho", "Q33268") # Bhojpuri

    # Languages of the European Union
    de_ = Language("de", "Q183") # German
    en_ = Language("en", "Q1860") # English
    es_ = Language("es", "Q1321") # Spanish
    fr_ = Language("fr", "Q150") # French
    it_ = Language("it", "Q652") # Italian
    pt_ = Language("pt", "Q5146") # Portuguese

    # Other Eighth Schedule languages
    hi_ = Language("hi", "Q11051") # Hindustani (deva)
    ur_ = Language("ur", "Q11051") # Hindustani (aran)
    pa_ = Language("pa", "Q58635") # Punjabi (guru)
    pnb_ = Language("pnb", "Q58635") # Punjabi (aran)
    gu_ = Language("gu", "Q5137") # Gujarati
    ta_ = Language("ta", "Q5885") # Tamil
    te_ = Language("te", "Q8097") # Telugu
    kn_ = Language("kn", "Q33673") # Kannada
    ml_ = Language("ml", "Q36236") # Malayalam
    ks_deva_ = Language("ks-deva", "Q33552") # Kashmiri
    ks_arab_ = Language("ks-arab", "Q33552")
    gom_deva_ = Language("gom-deva", "Q5575236") # Goan Konkani
    gom_latn_ = Language("gom-latn", "Q5575236")
    
    # Other languages of India
    
    
    # Other languages of note
    
