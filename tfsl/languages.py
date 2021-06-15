from collections import defaultdict
from functools import singledispatchmethod

import tfsl.lexeme
import tfsl.monolingualtext
import tfsl.utils


class Language:
    """ Container for languages.
        Note that due to their use literally anywhere a language is expected,
        the item should remain a string.
    """
    def __init__(self, code: str, item: str):
        self.code = code
        self.item = item

    def __repr__(self):
        return f'{self.code} ({self.item})'

    def __eq__(self, rhs):
        return self.compare_eq(rhs)

    def __rmatmul__(self, text):
        return self.rmatmul(text)

    @singledispatchmethod
    def rmatmul(self, arg):
        raise NotImplementedError(f"Can't apply language to {type(arg)}")

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


class Languages:
    """ Mapping of BCP47 codes used on Wikimedia projects to Language objects.
        Only those whose codes are available either as termbox codes, monolingual text codes,
        or separate lexeme language codes should have entries here.
        (Dashes, if present in a code, should be substituted with underscores here.)
    """
    __itemlookup__ = defaultdict(list)
    __codelookup__ = defaultdict(list)

    # TODO: everywhere this method is called, find a way to specify among results if multiple found
    @classmethod
    def find(cls, string_in):
        if tfsl.utils.matches_item(string_in):
            return cls.__itemlookup__[string_in]
        else:
            return cls.__codelookup__[string_in]

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if(type(value) == Language):
            self.__itemlookup__[value.item].append(value)
            self.__codelookup__[value.code].append(value)


langs = Languages()


def get_first_lang(arg):
    return langs.find(arg)[0]


# Eastern Indo-Aryan languages
langs.bn_ = Language("bn", "Q9610")  # Bengali
langs.ctg_ = Language("ctg", "Q33173")  # Chittagonian
langs.rkt_ = Language("rkt", "Q3241618")  # Rangpuri
langs.syl_ = Language("syl", "Q2044560")  # Sylheti
langs.ccp_ = Language("ccp", "Q32952")  # Chakma
langs.rhg_rohg_ = Language("rhg-rohg", "Q3241177")  # Rohingya
langs.as_ = Language("as", "Q29401")  # Assamese
langs.or_ = Language("or", "Q33810")  # Odia
langs.bho_ = Language("bho", "Q33268")  # Bhojpuri

# multiple languages -- export using this to Wikidata might fail
langs.mul_ = Language("mul", "Q20923490")

# Languages of the United Nations
langs.en_ = Language("en", "Q1860")  # English
langs.es_ = Language("es", "Q1321")  # Spanish
langs.fr_ = Language("fr", "Q150")  # French
langs.ru_ = Language("ru", "Q7737")  # Russian
langs.ar_ = Language("ar", "Q13955")  # Arabic (Modern Standard)
langs.zh_ = Language("zh", "Q9192")  # Mandarin Chinese

# Languages of the European Union
langs.bg_ = Language("bg", "Q7918")  # Bulgarian
# omitting Croatian for now pending resolution on handling of Shtokavian standards
langs.cs_ = Language("cs", "Q9056")  # Czech
langs.da_ = Language("da", "Q9035")  # Danish
langs.de_ = Language("de", "Q183")  # German
langs.el_ = Language("el", "Q36510")  # Greek
langs.et_ = Language("et", "Q9072")  # Estonian
langs.fi_ = Language("fi", "Q1412")  # Finnish
langs.ga_ = Language("ga", "Q9142")  # Irish
langs.hu_ = Language("hu", "Q9067")  # Hungarian
langs.it_ = Language("it", "Q652")  # Italian
langs.lt_ = Language("lt", "Q9083")  # Lithuanian
langs.lv_ = Language("lv", "Q9078")  # Latvian
langs.mt_ = Language("mt", "Q9166")  # Maltese
langs.nl_ = Language("nl", "Q7411")  # Dutch
langs.pl_ = Language("pl", "Q809")  # Polish
langs.pt_ = Language("pt", "Q5146")  # Portuguese
langs.ro_ = Language("ro", "Q7913")  # Romanian
langs.sk_ = Language("sk", "Q9058")  # Slovak
langs.sl_ = Language("sl", "Q9063")  # Slovene
langs.sv_ = Language("sv", "Q9027")  # Swedish

# Other Eighth Schedule languages (Bengali, Assamese, Odia are above)
# omitting Bodo for now pending script choices
# omitting Dogri for now pending script choices
langs.gu_ = Language("gu", "Q5137")  # Gujarati
langs.hi_ = Language("hi", "Q11051")  # Hindustani (deva)
langs.kn_ = Language("kn", "Q33673")  # Kannada
langs.ks_deva_ = Language("ks-deva", "Q33552")  # Kashmiri
langs.ks_arab_ = Language("ks-arab", "Q33552")
langs.gom_deva_ = Language("gom-deva", "Q5575236")  # Goan Konkani
langs.gom_latn_ = Language("gom-latn", "Q5575236")
langs.mai_ = Language("mai", "Q36109")  # Maithili
langs.ml_ = Language("ml", "Q36236")  # Malayalam
langs.mni_ = Language("mni", "Q33868")  # Meitei
langs.mr_ = Language("mr", "Q1571")  # Marathi
langs.ne_ = Language("ne", "Q33823")  # Nepali
langs.pa_ = Language("pa", "Q58635")  # Punjabi (guru)
langs.pnb_ = Language("pnb", "Q58635")  # Punjabi (aran)
langs.sa_ = Language("sa", "Q11059")  # Sanskrit
langs.sat_ = Language("sat", "Q33965")  # Santali (olck)
langs.sat_beng_ = Language("sat-beng", "Q33965")  # Santali
langs.sat_latn_ = Language("sat-latn", "Q33965")  # Santali
langs.sat_orya_ = Language("sat-orya", "Q33965")  # Santali
langs.sd_ = Language("sd", "Q33997")  # Sindhi (aran)
# omitting sd-deva for now pending script request
langs.ta_ = Language("ta", "Q5885")  # Tamil
langs.te_ = Language("te", "Q8097")  # Telugu
langs.ur_ = Language("ur", "Q11051")  # Hindustani (aran)

# other languages from the Nordic Council area
langs.is_ = Language("is", "Q294")  # Icelandic
langs.nb_ = Language("nb", "Q25167")  # Bokmål
langs.nn_ = Language("nn", "Q25164")  # Nynorsk
langs.kl_ = Language("kl", "Q25355")  # Kalaallisut
langs.fo_ = Language("fo", "Q25258")  # Faroese
langs.sjd_ = Language("sjd", "Q33656")  # Kildin Sami
langs.se_ = Language("se", "Q33947")  # Northern Sami
langs.smn_ = Language("smn", "Q33462")  # Inari Sami
langs.sms_ = Language("sms", "Q13271")  # Skolt Sami
langs.smj_ = Language("smj", "Q56322")  # Lule Sami
langs.sje_ = Language("sje", "Q56314")  # Pite Sami
langs.sju_ = Language("sju", "Q56415")  # Ume Sami
langs.sma_ = Language("sma", "Q13293")  # Southern Sami

# other languages (in general)
langs.pwn_ = Language("pwn", "Q715755")  # Paiwan
