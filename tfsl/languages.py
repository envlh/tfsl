from collections import defaultdict
from functools import singledispatchmethod

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
        if rhs[0] == "Q":
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
        if isinstance(value, Language):
            self.__itemlookup__[value.item].append(value)
            self.__codelookup__[value.code].append(value)


langs = Languages()


def get_first_lang(arg):
    try:
        return langs.find(arg)[0]
    except IndexError as e:
        raise Exception('Could not find', arg) from e

# pylint: disable=attribute-defined-outside-init

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
langs.cs_ = Language("cs", "Q9056")  # Czech
langs.da_ = Language("da", "Q9035")  # Danish
langs.de_ = Language("de", "Q188")  # German
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
langs.af_ = Language("af", "Q14196")  # Afrikaans
langs.ast_ = Language("ast", "Q29507")  # Asturian
langs.az_ = Language("az", "Q9292")  # Azerbaijani
langs.be_ = Language("be", "Q9091")  # Belarusian
langs.be_tarask_ = Language("be-tarask", "Q9091")  # Taraskievica
langs.ca_ = Language("ca", "Q7026")  # Catalan
langs.cy_ = Language("cy", "Q9309")  # Welsh
langs.dag_ = Language("dag", "Q32238")  # Dagbani
langs.dsb_ = Language("dsb", "Q13286")  # Lower Sorbian
langs.de_at_ = Language("de-at", "Q306626")  # Austrian German
langs.de_ch_ = Language("de-ch", "Q387066")  # Austrian German
langs.en_gb_ = Language("en-gb", "Q7979")  # British English
langs.eo_ = Language("eo", "Q143")  # Esperanto
langs.eu_ = Language("eu", "Q8752")  # Basque
langs.fa_ = Language("fa", "Q9168")  # Persian
langs.gd_ = Language("gd", "Q9314")  # Scottish Gaelic
langs.gl_ = Language("gl", "Q9307")  # Galician
langs.ha_ = Language("ha", "Q56475")  # Hausa
langs.ha_arab_ = Language("ha-arab", "Q56475")  # Hausa
langs.he_ = Language("he", "Q9288")  # Hebrew
langs.hsb_ = Language("hsb", "Q13248")  # Upper Sorbian
langs.hy_ = Language("hy", "Q8785")  # Armenian
langs.ig_ = Language("ig", "Q33578")  # Igbo
langs.io_ = Language("io", "Q35224")  # Ido
langs.ja_ = Language("ja", "Q5287")  # Japanese
langs.jv_ = Language("jv", "Q33549")  # Javanese
langs.ka_ = Language("ka", "Q8108")  # Georgian
langs.kk_ = Language("kk", "Q9252")  # Kazakh
langs.ko_ = Language("ko", "Q9176")  # Korean
langs.la_ = Language("la", "Q397")  # Latin
langs.lfn_ = Language("lfn", "Q146803")  # Lingua Franca Nova
langs.mk_ = Language("mk", "Q9296")  # Macedonian
langs.ms_ = Language("ms", "Q9237")  # Malay
langs.nan_ = Language("nan", "Q36495")  # Southern Min
langs.nqo_ = Language("nqo", "Q35772")  # Manding languages
langs.oc_ = Language("oc", "Q14185")  # Occitan
langs.pi_ = Language("pi", "Q36727")  # Pali
langs.ps_ = Language("ps", "Q58680")  # Pashto
langs.pt_br_ = Language("pt-br", "Q750553")  # Brazilian Portuguese
langs.pwn_ = Language("pwn", "Q715755")  # Paiwan
langs.rm_ = Language("rm", "Q13199")  # Romansh
langs.scn_ = Language("scn", "Q33973")  # Sicilian
langs.sco_ = Language("sco", "Q14549")  # Scots
langs.ss_ = Language("ss", "Q34014")  # Swazi
langs.tg_ = Language("tg", "Q9260")  # Tajik
langs.th_ = Language("th", "Q9217")  # Thai
langs.tr_ = Language("tr", "Q256")  # Turkish
langs.udm_ = Language("udm", "Q13238")  # Udmurt
langs.uk_ = Language("uk", "Q8798")  # Ukrainian
langs.vi_ = Language("vi", "Q9199")  # Vietnamese
langs.vmf_ = Language("vmf", "Q71223")  # East Franconian
langs.vo_ = Language("vo", "Q36986")  # Volapuk
langs.zxx_ = Language("zxx", "Q22282939")  # no linguistic content

# Lahjas and Darjas
langs.arq_ = Language("arq", "Q56499")  # Algerian
langs.arz_ = Language("arz", "Q29919")  # Egyptian
# Shtokavian variants
langs.hr_ = Language("hr", "Q6654")  # Croatian
langs.sr_ = Language("sr", "Q9299")  # Serbian
langs.sr_ec_ = Language("sr-ec", "Q9299")  # Serbian written in Cyrillic
# certain languages of Southeast Asia
langs.id_ = Language("id", "Q9240")  # Indonesian
# certain languages of East Asia
langs.zh_ = Language("zh", "Q9192")  # Mandarin
langs.zh_cn_ = Language("zh-cn", "Q9192")  # Mandarin (Mainland)
langs.zh_hans_ = Language("zh-hans", "Q9192")  # Mandarin (Simplified)
langs.zh_hant_ = Language("zh-hant", "Q9192")  # Mandarin (Traditional)
langs.zh_tw_ = Language("zh-tw", "Q9192")  # Mandarin (Taiwan)
