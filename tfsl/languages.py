""" Holds the Language class and a Languages class with some language objects already defined within. """

from collections import defaultdict
from functools import singledispatchmethod
from typing import Any, DefaultDict, List

import tfsl.interfaces as I
import tfsl.monolingualtext
import tfsl.utils

class Language:
    """ Container for languages.
        Note that due to their use literally anywhere a language is expected,
        the item should remain a string.
    """
    def __init__(self, code: str, item: str):
        self.code = I.LanguageCode(code)
        if I.is_Qid(item):
            self.item: I.Qid = item
        else:
            raise ValueError(f"{item} is not a Qid")

    def __repr__(self) -> str:
        return f'{self.code} ({self.item})'

    def __eq__(self, rhs: object) -> bool:
        return self.compare_eq(rhs)

    def __rmatmul__(self, arg: object) -> 'tfsl.monolingualtext.MonolingualText':
        if isinstance(arg, str):
            return tfsl.monolingualtext.MonolingualText(arg, self)
        elif isinstance(arg, tfsl.monolingualtext.MonolingualText):
            return tfsl.monolingualtext.MonolingualText(arg.text, self)
        raise NotImplementedError(f"Can't apply language to {type(arg)}")

    @singledispatchmethod
    def compare_eq(self, rhs: object) -> bool:
        """ Equality comparison between this Language and something else. """
        if not isinstance(rhs, Language):
            return NotImplemented
        return self.item == rhs.item and self.code == rhs.code

    @compare_eq.register
    def _(self, rhs: str) -> bool:
        if rhs[0] == "Q":
            return self.item == rhs
        return self.code == rhs

    def __hash__(self) -> int:
        return hash((self.code, self.item))

class Languages:
    """ Mapping of BCP47 codes used on Wikimedia projects to Language objects.
        Only those whose codes are available either as termbox codes, monolingual text codes,
        or separate lexeme language codes should have entries here.
        (Dashes, if present in a code, should be substituted with underscores here.)
    """
    __itemlookup__: DefaultDict[I.Qid, List[Language]] = defaultdict(list)
    __codelookup__: DefaultDict[str, List[Language]] = defaultdict(list)

    # TODO: everywhere this method is called, find a way to specify among results if multiple found
    @classmethod
    def find(cls, string_in: str) -> List[Language]:
        """ If the input is a Qid, finds the languages with that Qid as the item;
            otherwise finds the languages with the input as the language code.
        """
        if I.is_Qid(string_in):
            return cls.__itemlookup__[string_in]
        else:
            return cls.__codelookup__[string_in]

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if isinstance(value, Language):
            self.__itemlookup__[value.item].append(value)
            self.__codelookup__[value.code].append(value)

    def __init__(self) -> None:
        self.mul_ = Language("mul", "Q20923490")  #! multiple languages -- export using this to Wikidata might fail
        self.zxx_ = Language("zxx", "Q22282939")  #! no linguistic content
        self.mis_ = Language("mis", "Q22283016")  #! language without a specific language code
        self.und_ = Language("und", "Q22283016")  #! undetermined language

        # Eastern Indo-Aryan languages
        self.bn_ = Language("bn", "Q9610")  # Bengali
        self.ctg_ = Language("ctg", "Q33173")  # Chittagonian
        self.rkt_ = Language("rkt", "Q3241618")  # Rangpuri
        self.syl_ = Language("syl", "Q2044560")  # Sylheti
        self.ccp_ = Language("ccp", "Q32952")  # Chakma
        self.rhg_rohg_ = Language("rhg-rohg", "Q3241177")  # Rohingya
        self.as_ = Language("as", "Q29401")  # Assamese
        self.or_ = Language("or", "Q33810")  # Odia
        self.bho_ = Language("bho", "Q33268")  # Bhojpuri

        # Languages of the United Nations
        self.en_ = Language("en", "Q1860")  # English
        self.es_ = Language("es", "Q1321")  # Spanish
        self.fr_ = Language("fr", "Q150")  # French
        self.ru_ = Language("ru", "Q7737")  # Russian
        self.ar_ = Language("ar", "Q13955")  # Arabic (Modern Standard)
        self.zh_ = Language("zh", "Q9192")  # Mandarin Chinese

        # Languages of the European Union
        self.bg_ = Language("bg", "Q7918")  # Bulgarian
        self.cs_ = Language("cs", "Q9056")  # Czech
        self.da_ = Language("da", "Q9035")  # Danish
        self.de_ = Language("de", "Q188")  # German
        self.el_ = Language("el", "Q36510")  # Greek
        self.et_ = Language("et", "Q9072")  # Estonian
        self.fi_ = Language("fi", "Q1412")  # Finnish
        self.ga_ = Language("ga", "Q9142")  # Irish
        self.hu_ = Language("hu", "Q9067")  # Hungarian
        self.it_ = Language("it", "Q652")  # Italian
        self.lt_ = Language("lt", "Q9083")  # Lithuanian
        self.lv_ = Language("lv", "Q9078")  # Latvian
        self.mt_ = Language("mt", "Q9166")  # Maltese
        self.nl_ = Language("nl", "Q7411")  # Dutch
        self.pl_ = Language("pl", "Q809")  # Polish
        self.pt_ = Language("pt", "Q5146")  # Portuguese
        self.ro_ = Language("ro", "Q7913")  # Romanian
        self.sk_ = Language("sk", "Q9058")  # Slovak
        self.sl_ = Language("sl", "Q9063")  # Slovene
        self.sv_ = Language("sv", "Q9027")  # Swedish

        # Other Eighth Schedule languages (Bengali, Assamese, Odia are above)
        # omitting Bodo for now pending script choices
        # omitting Dogri for now pending script choices
        self.gu_ = Language("gu", "Q5137")  # Gujarati
        self.hi_ = Language("hi", "Q11051")  # Hindustani (deva)
        self.kn_ = Language("kn", "Q33673")  # Kannada
        self.ks_deva_ = Language("ks-deva", "Q33552")  # Kashmiri
        self.ks_arab_ = Language("ks-arab", "Q33552")
        self.gom_deva_ = Language("gom-deva", "Q5575236")  # Goan Konkani
        self.gom_latn_ = Language("gom-latn", "Q5575236")
        self.mai_ = Language("mai", "Q36109")  # Maithili
        self.ml_ = Language("ml", "Q36236")  # Malayalam
        self.mni_ = Language("mni", "Q33868")  # Meitei
        self.mr_ = Language("mr", "Q1571")  # Marathi
        self.ne_ = Language("ne", "Q33823")  # Nepali
        self.pa_ = Language("pa", "Q58635")  # Punjabi (guru)
        self.pnb_ = Language("pnb", "Q58635")  # Punjabi (aran)
        self.sa_ = Language("sa", "Q11059")  # Sanskrit
        self.sat_ = Language("sat", "Q33965")  # Santali (olck)
        self.sat_beng_ = Language("sat-beng", "Q33965")  # Santali
        self.sat_latn_ = Language("sat-latn", "Q33965")  # Santali
        self.sat_orya_ = Language("sat-orya", "Q33965")  # Santali
        self.sd_ = Language("sd", "Q33997")  # Sindhi (aran)
        # omitting sd-deva for now pending script request
        self.ta_ = Language("ta", "Q5885")  # Tamil
        self.te_ = Language("te", "Q8097")  # Telugu
        self.ur_ = Language("ur", "Q11051")  # Hindustani (aran)

        # other languages from the Nordic Council area
        self.is_ = Language("is", "Q294")  # Icelandic
        self.nb_ = Language("nb", "Q25167")  # Bokmål
        self.nn_ = Language("nn", "Q25164")  # Nynorsk
        self.kl_ = Language("kl", "Q25355")  # Kalaallisut
        self.fo_ = Language("fo", "Q25258")  # Faroese
        self.sjd_ = Language("sjd", "Q33656")  # Kildin Sami
        self.se_ = Language("se", "Q33947")  # Northern Sami
        self.smn_ = Language("smn", "Q33462")  # Inari Sami
        self.sms_ = Language("sms", "Q13271")  # Skolt Sami
        self.smj_ = Language("smj", "Q56322")  # Lule Sami
        self.sje_ = Language("sje", "Q56314")  # Pite Sami
        self.sju_ = Language("sju", "Q56415")  # Ume Sami
        self.sma_ = Language("sma", "Q13293")  # Southern Sami

        # other languages (in general)
        self.af_ = Language("af", "Q14196")  # Afrikaans
        self.ast_ = Language("ast", "Q29507")  # Asturian
        self.az_ = Language("az", "Q9292")  # Azerbaijani
        self.ba_ = Language("ba", "Q13389")  # Bashkir
        self.bar_ = Language("bar", "Q29540")  # Bavarian
        self.be_ = Language("be", "Q9091")  # Belarusian
        self.be_tarask_ = Language("be-tarask", "Q9091")  # Taraskievica
        self.br_ = Language("br", "Q12107")  # Breton
        self.ca_ = Language("ca", "Q7026")  # Catalan
        self.cy_ = Language("cy", "Q9309")  # Welsh
        self.dag_ = Language("dag", "Q32238")  # Dagbani
        self.dsb_ = Language("dsb", "Q13286")  # Lower Sorbian
        self.de_at_ = Language("de-at", "Q306626")  # Austrian German
        self.de_ch_ = Language("de-ch", "Q387066")  # Swiss German
        self.en_gb_ = Language("en-gb", "Q7979")  # British English
        self.eo_ = Language("eo", "Q143")  # Esperanto
        self.eu_ = Language("eu", "Q8752")  # Basque
        self.fa_ = Language("fa", "Q9168")  # Persian
        self.fy_ = Language("fy", "Q27175")  # West Frisian
        self.gd_ = Language("gd", "Q9314")  # Scottish Gaelic
        self.gl_ = Language("gl", "Q9307")  # Galician
        self.gn_ = Language("gn", "Q35876")  # Guarani
        self.ha_ = Language("ha", "Q56475")  # Hausa
        self.ha_arab_ = Language("ha-arab", "Q56475")  # Hausa
        self.he_ = Language("he", "Q9288")  # Hebrew
        self.hsb_ = Language("hsb", "Q13248")  # Upper Sorbian
        self.hy_ = Language("hy", "Q8785")  # Armenian
        self.ig_ = Language("ig", "Q33578")  # Igbo
        self.io_ = Language("io", "Q35224")  # Ido
        self.ja_ = Language("ja", "Q5287")  # Japanese
        self.jv_ = Language("jv", "Q33549")  # Javanese
        self.ka_ = Language("ka", "Q8108")  # Georgian
        self.kk_ = Language("kk", "Q9252")  # Kazakh
        self.ko_ = Language("ko", "Q9176")  # Korean
        self.kw_ = Language("kw", "Q25289")  # Cornish
        self.la_ = Language("la", "Q397")  # Latin
        self.lb_ = Language("lb", "Q9051")  # Luxembourgish
        self.lfn_ = Language("lfn", "Q146803")  # Lingua Franca Nova
        self.mk_ = Language("mk", "Q9296")  # Macedonian
        self.ms_ = Language("ms", "Q9237")  # Malay
        self.ms_arab_ = Language("ms-arab", "Q9237")  # Malay (Jawi)
        self.myv_ = Language("myv", "Q29952")  # Erzya
        self.nan_ = Language("nan", "Q36495")  # Southern Min
        self.nqo_ = Language("nqo", "Q35772")  # Manding languages
        self.oc_ = Language("oc", "Q14185")  # Occitan
        self.olo_ = Language("olo", "Q36584")  # Livvi-Karelian
        self.pi_ = Language("pi", "Q36727")  # Pali
        self.ps_ = Language("ps", "Q58680")  # Pashto
        self.pt_br_ = Language("pt-br", "Q750553")  # Brazilian Portuguese
        self.pwn_ = Language("pwn", "Q715755")  # Paiwan
        self.rm_ = Language("rm", "Q13199")  # Romansh
        self.scn_ = Language("scn", "Q33973")  # Sicilian
        self.sco_ = Language("sco", "Q14549")  # Scots
        self.sq_ = Language("sq", "Q8748")  # Albanian
        self.ss_ = Language("ss", "Q34014")  # Swazi
        self.tg_ = Language("tg", "Q9260")  # Tajik
        self.th_ = Language("th", "Q9217")  # Thai
        self.tr_ = Language("tr", "Q256")  # Turkish
        self.tw_ = Language("tw", "Q36850")  # Twi
        self.udm_ = Language("udm", "Q13238")  # Udmurt
        self.uk_ = Language("uk", "Q8798")  # Ukrainian
        self.vep_ = Language("vep", "Q32747")  # Veps
        self.vi_ = Language("vi", "Q9199")  # Vietnamese
        self.vmf_ = Language("vmf", "Q71223")  # East Franconian
        self.vo_ = Language("vo", "Q36986")  # Volapuk
        self.wa_ = Language("wa", "Q34219")  # Walloon

        # languages that should be deleted from Wikimedia projects soon
        self.no_ = Language("no", "Q9043")  # Norwegian
        self.zh_classical_ = Language("zh-classical", "Q37041")  # Classical Chinese
        self.zh_min_nan_ = Language("zh-min-nan", "Q36495")  # Chinese (Min Nan)
        self.zh_yue_ = Language("zh-yue", "Q7033959")  # Cantonese
        # Lahjas and Darjas
        self.aeb_ = Language("aeb", "Q56240")  # Tunisian
        self.aeb_arab_ = Language("aeb-arab", "Q56240")  # Tunisian
        self.aeb_latn_ = Language("aeb-latn", "Q56240")  # Tunisian
        self.arq_ = Language("arq", "Q56499")  # Algerian
        self.ary_ = Language("ary", "Q56426")  # Moroccan
        self.arz_ = Language("arz", "Q29919")  # Egyptian
        # Shtokavian variants
        self.bs_ = Language("bs", "Q9303")  # Bosnian
        self.hr_ = Language("hr", "Q6654")  # Croatian
        self.sh_ = Language("sh", "Q9301")  # Serbo-Croatian
        self.sr_ = Language("sr", "Q9299")  # Serbian
        self.sr_ec_ = Language("sr-ec", "Q9299")  # Serbian written in Cyrillic
        self.sr_el_ = Language("sr-el", "Q9299")  # Serbian (Latin script)
        # certain languages of Southeast Asia
        self.id_ = Language("id", "Q9240")  # Indonesian
        # certain languages of East Asia
        self.zh_cn_ = Language("zh-cn", "Q9192")  # Mandarin (Mainland)
        self.zh_hans_ = Language("zh-hans", "Q9192")  # Mandarin (Simplified)
        self.zh_hant_ = Language("zh-hant", "Q9192")  # Mandarin (Traditional)
        self.zh_hk_ = Language("zh-hk", "Q9192")  # Chinese (Hong Kong)
        self.zh_mo_ = Language("zh-mo", "Q9192")  # Chinese (Macau)
        self.zh_my_ = Language("zh-my", "Q9192")  # Chinese (Malaysia)
        self.zh_sg_ = Language("zh-sg", "Q9192")  # Chinese (Singapore)
        self.zh_tw_ = Language("zh-tw", "Q9192")  # Mandarin (Taiwan)

        # TODO: clean up the giant mess below, imported from the label languages list
        self.aa_ = Language("aa", "Q27811")  # Afar
        self.ab_ = Language("ab", "Q5111")  # Abkhazian
        self.abs_ = Language("abs", "Q3124354")  # Ambonese Malay
        self.ace_ = Language("ace", "Q27683")  # Achinese
        self.ady_ = Language("ady", "Q27776")  # Adyghe
        self.ady_cyrl_ = Language("ady-cyrl", "Q27776")  # Adyghe (Cyrillic script)
        self.agq_ = Language("agq", "Q34737")  # Aghem
        self.ak_ = Language("ak", "Q28026")  # Akan
        self.aln_ = Language("aln", "Q181037")  # Gheg Albanian
        self.als_ = Language("als", "Q131339")  # Alemannisch
        self.alt_ = Language("alt", "Q1991779")  # Southern Altai
        self.am_ = Language("am", "Q28244")  # Amharic
        self.ami_ = Language("ami", "Q35132")  # Amis
        self.an_ = Language("an", "Q8765")  # Aragonese
        self.ang_ = Language("ang", "Q42365")  # Old English
        self.anp_ = Language("anp", "Q28378")  # Angika
        self.arc_ = Language("arc", "Q28602")  # Aramaic
        self.arn_ = Language("arn", "Q33730")  # Mapuche
        self.ase_ = Language("ase", "Q14759")  # American Sign Language
        self.atj_ = Language("atj", "Q56590")  # Atikamekw
        self.av_ = Language("av", "Q29561")  # Avaric
        self.avk_ = Language("avk", "Q1377116")  # Kotava
        self.awa_ = Language("awa", "Q29579")  # Awadhi
        self.ay_ = Language("ay", "Q4627")  # Aymara
        self.azb_ = Language("azb", "Q9292")  # South Azerbaijani
        self.bag_ = Language("bag", "Q36621")  # Tuki
        self.ban_ = Language("ban", "Q33070")  # Balinese
        self.ban_bali_ = Language("ban-bali", "Q33070")  # ᬩᬲᬩᬮᬶ
        self.bas_ = Language("bas", "Q33093")  # Basaa
        self.bat_smg_ = Language("bat-smg", "Q213434")  # Samogitian
        self.bax_ = Language("bax", "Q35280")  # Bamun
        self.bbc_ = Language("bbc", "Q33017")  # Batak Toba
        self.bbc_latn_ = Language("bbc-latn", "Q33017")  # Batak Toba (Latin script)
        self.bbj_ = Language("bbj", "Q35271")  # Ghomala
        self.bcc_ = Language("bcc", "Q12634001")  # Southern Balochi
        self.bcl_ = Language("bcl", "Q33284")  # Central Bikol
        self.be_x_old_ = Language("be-x-old", "Q9091")  # Belarusian (Taraškievica orthography)
        self.bgn_ = Language("bgn", "Q12645561")  # Western Balochi
        self.bh_ = Language("bh", "Q33268")  # Bhojpuri
        self.bi_ = Language("bi", "Q35452")  # Bislama
        self.bjn_ = Language("bjn", "Q33151")  # Banjar
        self.bkc_ = Language("bkc", "Q34905")  # Baka
        self.bkh_ = Language("bkh", "Q34866")  # Bakako
        self.bkm_ = Language("bkm", "Q1656595")  # Kom
        self.bm_ = Language("bm", "Q33243")  # Bambara
        self.bo_ = Language("bo", "Q34271")  # Tibetan
        self.bpy_ = Language("bpy", "Q37059")  # Bishnupriya
        self.bqi_ = Language("bqi", "Q257829")  # Bakhtiari
        self.brh_ = Language("brh", "Q33202")  # Brahui
        self.btm_ = Language("btm", "Q2891049")  # Batak Mandailing
        self.bto_ = Language("bto", "Q12633026")  # Iriga Bicolano
        self.bug_ = Language("bug", "Q33190")  # Buginese
        self.bxr_ = Language("bxr", "Q16116629")  # Russia Buriat
        self.byv_ = Language("byv", "Q36019")  # Medumba
        self.cak_ = Language("cak", "Q35115")  # Kaqchikel
        self.cbk_zam_ = Language("cbk-zam", "Q33281")  # Chavacano
        self.cdo_ = Language("cdo", "Q36455")  # Min Dong Chinese
        self.ce_ = Language("ce", "Q33350")  # Chechen
        self.ceb_ = Language("ceb", "Q33239")  # Cebuano
        self.ch_ = Language("ch", "Q33262")  # Chamorro
        self.cho_ = Language("cho", "Q32979")  # Choctaw
        self.chr_ = Language("chr", "Q33388")  # Cherokee
        self.chy_ = Language("chy", "Q33265")  # Cheyenne
        self.ckb_ = Language("ckb", "Q36811")  # Central Kurdish
        self.co_ = Language("co", "Q33111")  # Corsican
        self.cps_ = Language("cps", "Q2937525")  # Capiznon
        self.cr_ = Language("cr", "Q33390")  # Cree
        self.crh_ = Language("crh", "Q33357")  # Crimean Tatar
        self.crh_cyrl_ = Language("crh-cyrl", "Q33357")  # Crimean Tatar (Cyrillic script)
        self.crh_latn_ = Language("crh-latn", "Q33357")  # Crimean Tatar (Latin script)
        self.csb_ = Language("csb", "Q33690")  # Kashubian
        self.cu_ = Language("cu", "Q35499")  # Church Slavic
        self.cv_ = Language("cv", "Q33348")  # Chuvash
        self.de_1901_ = Language("de-1901", "Q188") # German (1901 to 1996)
        self.de_formal_ = Language("de-formal", "Q188")  # German (formal address)
        self.din_ = Language("din", "Q56466")  # Dinka
        self.diq_ = Language("diq", "Q10199")  # Zazaki
        self.dtp_ = Language("dtp", "Q5317225")  # Central Dusun
        self.dty_ = Language("dty", "Q18415595")  # Doteli
        self.dua_ = Language("dua", "Q33013")  # Duala
        self.dv_ = Language("dv", "Q32656")  # Divehi
        self.dz_ = Language("dz", "Q33081")  # Dzongkha
        self.ee_ = Language("ee", "Q30005")  # Ewe
        self.egl_ = Language("egl", "Q1057898")  # Emilian
        self.eml_ = Language("eml", "Q242648")  # Emiliano-Romagnolo
        self.en_ca_ = Language("en-ca", "Q44676")  # Canadian English
        self.en_us_ = Language("en-us", "Q7976")  # American English
        self.es_419_ = Language("es-419", "Q56649449")  # Latin American Spanish
        self.es_formal_ = Language("es-formal", "Q1321")  # Spanish (formal address)
        self.eto_ = Language("eto", "Q35317")  # Eton
        self.etu_ = Language("etu", "Q35296")  # Ejagham
        self.ewo_ = Language("ewo", "Q35459")  # Ewondo
        self.ext_ = Language("ext", "Q30007")  # Extremaduran
        self.ff_ = Language("ff", "Q33454")  # Fulah
        self.fit_ = Language("fit", "Q13357")  # Tornedalen Finnish
        self.fj_ = Language("fj", "Q33295")  # Fijian
        self.fkv_ = Language("fkv", "Q165795")  # Kvensk
        self.fmp_ = Language("fmp", "Q35276")  # Fe'Fe'
        self.fon_ = Language("fon", "Q33291")  # Fon
        self.frc_ = Language("frc", "Q3083213")  # Cajun French
        self.frp_ = Language("frp", "Q15087")  # Arpitan
        self.frr_ = Language("frr", "Q28224")  # Northern Frisian
        self.fur_ = Language("fur", "Q33441")  # Friulian
        self.gaa_ = Language("gaa", "Q33287")  # Ga
        self.gag_ = Language("gag", "Q33457")  # Gagauz
        self.gan_ = Language("gan", "Q33475")  # Gan Chinese
        self.gan_hans_ = Language("gan-hans", "Q33475")  # Gan (Simplified)
        self.gan_hant_ = Language("gan-hant", "Q33475")  # Gan (Traditional)
        self.gcr_ = Language("gcr", "Q1363072")  # Guianan Creole
        self.gld_ = Language("gld", "Q13303")  # Nanai
        self.glk_ = Language("glk", "Q33657")  # Gilaki
        self.gom_ = Language("gom", "Q5575236")  # Goan Konkani
        self.gor_ = Language("gor", "Q2501174")  # Gorontalo
        self.got_ = Language("got", "Q35722")  # Gothic
        self.grc_ = Language("grc", "Q35497")  # Ancient Greek
        self.gsw_ = Language("gsw", "Q131339")  # Swiss German
        self.guc_ = Language("guc", "Q891085")  # Wayuu
        self.gur_ = Language("gur", "Q35331")  # Frafra
        self.guw_ = Language("guw", "Q3111668")  # Gun
        self.gv_ = Language("gv", "Q12175")  # Manx
        self.gya_ = Language("gya", "Q36594")  # Gbaya
        self.hak_ = Language("hak", "Q33375")  # Hakka Chinese
        self.haw_ = Language("haw", "Q33569")  # Hawaiian
        self.hif_ = Language("hif", "Q46728")  # Fiji Hindi
        self.hif_latn_ = Language("hif-latn", "Q46728")  # Fiji Hindi (Latin script)
        self.hil_ = Language("hil", "Q35978")  # Hiligaynon
        self.ho_ = Language("ho", "Q33617")  # Hiri Motu
        self.hrx_ = Language("hrx", "Q304049")  # Hunsrik
        self.hsn_ = Language("hsn", "Q13220")  # Xiang
        self.ht_ = Language("ht", "Q33491")  # Haitian Creole
        self.hu_formal_ = Language("hu-formal", "Q9067")  # Hungarian (formal address)
        self.hyw_ = Language("hyw", "Q180945")  # Western Armenian
        self.hz_ = Language("hz", "Q33315")  # Herero
        self.ia_ = Language("ia", "Q35934")  # Interlingua
        self.ie_ = Language("ie", "Q35850")  # Interlingue
        self.ii_ = Language("ii", "Q34235")  # Sichuan Yi
        self.ik_ = Language("ik", "Q27183")  # Inupiaq
        self.ike_cans_ = Language("ike-cans", "Q29921")  # Eastern Canadian (Aboriginal syllabics)
        self.ike_latn_ = Language("ike-latn", "Q29921")  # Eastern Canadian (Latin script)
        self.ilo_ = Language("ilo", "Q35936")  # Iloko
        self.inh_ = Language("inh", "Q33509")  # Ingush
        self.isu_ = Language("isu", "Q6089423")  # Isu
        self.iu_ = Language("iu", "Q29921")  # Inuktitut
        self.jam_ = Language("jam", "Q35939")  # Jamaican Creole English
        self.jbo_ = Language("jbo", "Q36350")  # Lojban
        self.jut_ = Language("jut", "Q1340322")  # Jutish
        self.kaa_ = Language("kaa", "Q33541")  # Kara-Kalpak
        self.kab_ = Language("kab", "Q35853")  # Kabyle
        self.kbd_ = Language("kbd", "Q33522")  # Kabardian
        self.kbd_cyrl_ = Language("kbd-cyrl", "Q33522")  # Kabardian (Cyrillic script)
        self.kbp_ = Language("kbp", "Q35475")  # Kabiye
        self.kcg_ = Language("kcg", "Q3912765")  # Tyap
        self.kea_ = Language("kea", "Q35963")  # Kabuverdianu
        self.ker_ = Language("ker", "Q56251")  # Kera
        self.kg_ = Language("kg", "Q33702")  # Kongo
        self.khw_ = Language("khw", "Q938216")  # Khowar
        self.ki_ = Language("ki", "Q33587")  # Kikuyu
        self.kiu_ = Language("kiu", "Q6023868")  # Kirmanjki
        self.kj_ = Language("kj", "Q1405077")  # Kuanyama
        self.kjp_ = Language("kjp", "Q5330390")  # Eastern Pwo
        self.kk_arab_ = Language("kk-arab", "Q9252")  # Kazakh (Arabic script)
        self.kk_cn_ = Language("kk-cn", "Q9252")  # Kazakh (China)
        self.kk_cyrl_ = Language("kk-cyrl", "Q9252")  # Kazakh (Cyrillic script)
        self.kk_kz_ = Language("kk-kz", "Q9252")  # Kazakh (Kazakhstan)
        self.kk_latn_ = Language("kk-latn", "Q9252")  # Kazakh (Latin script)
        self.kk_tr_ = Language("kk-tr", "Q9252")  # Kazakh (Turkey)
        self.km_ = Language("km", "Q9205")  # Khmer
        self.ko_kp_ = Language("ko-kp", "Q9176")  # Korean (North Korea)
        self.koi_ = Language("koi", "Q56318")  # Komi-Permyak
        self.kr_ = Language("kr", "Q36094")  # Kanuri
        self.krc_ = Language("krc", "Q33714")  # Karachay-Balkar
        self.kri_ = Language("kri", "Q35744")  # Krio
        self.krj_ = Language("krj", "Q33720")  # Kinaray-a
        self.krl_ = Language("krl", "Q33557")  # Karelian
        self.ks_ = Language("ks", "Q33552")  # Kashmiri
        self.ksf_ = Language("ksf", "Q34930")  # Bafia
        self.ksh_ = Language("ksh", "Q4624")  # Colognian
        self.ksw_ = Language("ksw", "Q56410")  # S'gaw Karen
        self.ku_ = Language("ku", "Q36163")  # Kurdish
        self.ku_arab_ = Language("ku-arab", "Q36163")  # Kurdish (Arabic script)
        self.ku_latn_ = Language("ku-latn", "Q36163")  # Kurdish (Latin script)
        self.kum_ = Language("kum", "Q36209")  # Kumyk
        self.kv_ = Language("kv", "Q36126")  # Komi
        self.ky_ = Language("ky", "Q9255")  # Kyrgyz
        self.lad_ = Language("lad", "Q36196")  # Ladino
        self.lbe_ = Language("lbe", "Q36206")  # Lak
        self.lem_ = Language("lem", "Q13479983")  # Nomaande
        self.lez_ = Language("lez", "Q31746")  # Lezghian
        self.lg_ = Language("lg", "Q33368")  # Ganda
        self.li_ = Language("li", "Q102172")  # Limburgish
        self.lij_ = Language("lij", "Q36106")  # Ligurian
        self.liv_ = Language("liv", "Q33698")  # Livonian
        self.lki_ = Language("lki", "Q56483")  # Laki
        self.lld_ = Language("lld", "Q36202")  # Ladin
        self.lmo_ = Language("lmo", "Q33754")  # Lombard
        self.ln_ = Language("ln", "Q36217")  # Lingala
        self.lns_ = Language("lns", "Q35788")  # Lamnso'
        self.lo_ = Language("lo", "Q9211")  # Lao
        self.loz_ = Language("loz", "Q33628")  # Lozi
        self.lrc_ = Language("lrc", "Q19933293")  # Northern Luri
        self.ltg_ = Language("ltg", "Q36212")  # Latgalian
        self.lus_ = Language("lus", "Q36147")  # Mizo
        self.luz_ = Language("luz", "Q12952748")  # Southern Luri
        self.lzh_ = Language("lzh", "Q37041")  # Literary Chinese
        self.lzz_ = Language("lzz", "Q1160372")  # Laz
        self.mad_ = Language("mad", "Q36213")  # Madurese
        self.map_bms_ = Language("map-bms", "Q33219")  # Basa Banyumasan
        self.mcn_ = Language("mcn", "Q56668")  # Massa
        self.mcp_ = Language("mcp", "Q35803")  # Maka
        self.mdf_ = Language("mdf", "Q13343")  # Moksha
        self.mg_ = Language("mg", "Q7930")  # Malagasy
        self.mh_ = Language("mh", "Q36280")  # Marshallese
        self.mhr_ = Language("mhr", "Q3906614")  # Eastern Mari
        self.mi_ = Language("mi", "Q36451")  # Maori
        self.min_ = Language("min", "Q13324")  # Minangkabau
        self.mn_ = Language("mn", "Q9246")  # Mongolian
        self.mnw_ = Language("mnw", "Q13349")  # Mon
        self.mo_ = Language("mo", "Q7913")  # Moldovan
        self.mrh_ = Language("mrh", "Q4175893")  # Mara
        self.mrj_ = Language("mrj", "Q1776032")  # Western Mari
        self.mua_ = Language("mua", "Q36032")  # Mundang
        self.mus_ = Language("mus", "Q523014")  # Muscogee
        self.mwl_ = Language("mwl", "Q13330")  # Mirandese
        self.my_ = Language("my", "Q9228")  # Burmese
        self.mzn_ = Language("mzn", "Q13356")  # Mazanderani
        self.na_ = Language("na", "Q13307")  # Nauru
        self.nah_ = Language("nah", "Q13300")  # Nāhuatl
        self.nan_hani_ = Language("nan-hani", "Q36495")  # Min Nan (Hanji)
        self.nap_ = Language("nap", "Q33845")  # Neapolitan
        self.nds_ = Language("nds", "Q25433")  # Low German
        self.nds_nl_ = Language("nds-nl", "Q25433")  # Low Saxon
        self.new_ = Language("new", "Q33979")  # Newari
        self.ng_ = Language("ng", "Q33900")  # Ndonga
        self.nia_ = Language("nia", "Q2407831")  # Nias
        self.niu_ = Language("niu", "Q33790")  # Niuean
        self.nl_informal_ = Language("nl-informal", "Q7411")  # Dutch (informal address)
        self.nla_ = Language("nla", "Q36292")  # Ngombala
        self.nmg_ = Language("nmg", "Q34098")  # Kwasio
        self.nmz_ = Language("nmz", "Q36085")  # Nawdm
        self.nnh_ = Language("nnh", "Q36286")  # Ngiemboon
        self.nod_ = Language("nod", "Q565110")  # Northern Thai
        self.nov_ = Language("nov", "Q36738")  # Novial
        self.nrm_ = Language("nrm", "Q33850")  # Norman
        self.nso_ = Language("nso", "Q33890")  # Northern Sotho
        self.nv_ = Language("nv", "Q13310")  # Navajo
        self.ny_ = Language("ny", "Q33273")  # Nyanja
        self.nys_ = Language("nys", "Q7049771")  # Nyungar
        self.ojb_ = Language("ojb", "Q7060356")  # Northwestern Ojibwe
        self.om_ = Language("om", "Q33864")  # Oromo
        self.os_ = Language("os", "Q33968")  # Ossetic
        self.osa_latn_ = Language("osa-latn", "Q2600085")  # Osage (Latin script)
        self.ota_ = Language("ota", "Q36730")  # Ottoman Turkish
        self.pag_ = Language("pag", "Q33879")  # Pangasinan
        self.pam_ = Language("pam", "Q36121")  # Pampanga
        self.pap_ = Language("pap", "Q33856")  # Papiamento
        self.pcd_ = Language("pcd", "Q34024")  # Picard
        self.pdc_ = Language("pdc", "Q22711")  # Pennsylvania German
        self.pdt_ = Language("pdt", "Q1751432")  # Plautdietsch
        self.pfl_ = Language("pfl", "Q23014")  # Palatine German
        self.pih_ = Language("pih", "Q36554")  # Norfuk / Pitkern
        self.pms_ = Language("pms", "Q15085")  # Piedmontese
        self.pnt_ = Language("pnt", "Q36748")  # Pontic
        self.prg_ = Language("prg", "Q35501")  # Prussian
        self.qu_ = Language("qu", "Q5218")  # Quechua
        self.quc_ = Language("quc", "Q36494")  # Kʼicheʼ
        self.qug_ = Language("qug", "Q12953845")  # Chimborazo Highland Quichua
        self.rgn_ = Language("rgn", "Q1641543")  # Romagnol
        self.rif_ = Language("rif", "Q34174")  # Riffian
        self.rmc_ = Language("rmc", "Q5045611")  # Carpathian Romani
        self.rmf_ = Language("rmf", "Q2093214")  # Finnish Kalo
        self.rmy_ = Language("rmy", "Q2669199")  # Vlax Romani
        self.rn_ = Language("rn", "Q33583")  # Rundi
        self.roa_rup_ = Language("roa-rup", "Q29316")  # Aromanian
        self.roa_tara_ = Language("roa-tara", "Q695526")  # Tarantino
        self.rue_ = Language("rue", "Q26245")  # Rusyn
        self.rup_ = Language("rup", "Q29316")  # Aromanian
        self.ruq_ = Language("ruq", "Q13358")  # Megleno-Romanian
        self.ruq_cyrl_ = Language("ruq-cyrl", "Q13358")  # Megleno-Romanian (Cyrillic script)
        self.ruq_latn_ = Language("ruq-latn", "Q13358")  # Megleno-Romanian (Latin script)
        self.rw_ = Language("rw", "Q33573")  # Kinyarwanda
        self.rwr_ = Language("rwr", "Q65455884")  # Marwari (India)
        self.ryu_ = Language("ryu", "Q34233")  # Okinawan
        self.sah_ = Language("sah", "Q34299")  # Sakha
        self.sc_ = Language("sc", "Q33976")  # Sardinian
        self.sdc_ = Language("sdc", "Q845441")  # Sassarese Sardinian
        self.sdh_ = Language("sdh", "Q1496597")  # Southern Kurdish
        self.sei_ = Language("sei", "Q36583")  # Seri
        self.ses_ = Language("ses", "Q35655")  # Koyraboro Senni
        self.sg_ = Language("sg", "Q33954")  # Sango
        self.sgs_ = Language("sgs", "Q213434")  # Samogitian
        self.shi_ = Language("shi", "Q34152")  # Tachelhit
        self.shi_latn_ = Language("shi-latn", "Q34152")  # Tachelhit (Latin script)
        self.shi_tfng_ = Language("shi-tfng", "Q34152")  # Tachelhit (Tifinagh script)
        self.shn_ = Language("shn", "Q56482")  # Shan
        self.shy_ = Language("shy", "Q33274")  # Shawiya
        self.shy_latn_ = Language("shy-latn", "Q33274")  # Shawiya (Latin script)
        self.si_ = Language("si", "Q13267")  # Sinhala
        self.simple_ = Language("simple", "Q1860")  # Simple English
        self.skr_ = Language("skr", "Q33902")  # Saraiki
        self.skr_arab_ = Language("skr-arab", "Q33902")  # Saraiki (Arabic script)
        self.sli_ = Language("sli", "Q152965")  # Lower Silesian
        self.sm_ = Language("sm", "Q34011")  # Samoan
        self.sn_ = Language("sn", "Q34004")  # Shona
        self.so_ = Language("so", "Q13275")  # Somali
        self.srn_ = Language("srn", "Q33989")  # Sranan Tongo
        self.srq_ = Language("srq", "Q3027953")  # Sirionó
        self.st_ = Language("st", "Q34340")  # Southern Sotho
        self.stq_ = Language("stq", "Q27154")  # Saterland Frisian
        self.sty_ = Language("sty", "Q4418344")  # Siberian Tatar
        self.su_ = Language("su", "Q34002")  # Sundanese
        self.sw_ = Language("sw", "Q7838")  # Swahili
        self.szl_ = Language("szl", "Q30319")  # Silesian
        self.szy_ = Language("szy", "Q718269")  # Sakizaya
        self.tay_ = Language("tay", "Q715766")  # Tayal
        self.tcy_ = Language("tcy", "Q34251")  # Tulu
        self.tet_ = Language("tet", "Q34125")  # Tetum
        self.tg_cyrl_ = Language("tg-cyrl", "Q9260")  # Tajik (Cyrillic script)
        self.tg_latn_ = Language("tg-latn", "Q9260")  # Tajik (Latin script)
        self.ti_ = Language("ti", "Q34124")  # Tigrinya
        self.tk_ = Language("tk", "Q9267")  # Turkmen
        self.tl_ = Language("tl", "Q34057")  # Tagalog
        self.tly_ = Language("tly", "Q34318")  # Talysh
        self.tly_cyrl_ = Language("tly-cyrl", "Q34318")  # толыши
        self.tn_ = Language("tn", "Q34137")  # Tswana
        self.to_ = Language("to", "Q34094")  # Tongan
        self.tpi_ = Language("tpi", "Q34159")  # Tok Pisin
        self.tru_ = Language("tru", "Q34040")  # Turoyo
        self.trv_ = Language("trv", "Q716686")  # Taroko
        self.ts_ = Language("ts", "Q34327")  # Tsonga
        self.tt_ = Language("tt", "Q25285")  # Tatar
        self.tt_cyrl_ = Language("tt-cyrl", "Q25285")  # Tatar (Cyrillic script)
        self.tt_latn_ = Language("tt-latn", "Q25285")  # Tatar (Latin script)
        self.tum_ = Language("tum", "Q34138")  # Tumbuka
        self.tvu_ = Language("tvu", "Q36632")  # Tunen
        self.ty_ = Language("ty", "Q34128")  # Tahitian
        self.tyv_ = Language("tyv", "Q34119")  # Tuvinian
        self.tzm_ = Language("tzm", "Q49741")  # Central Atlas Tamazight
        self.ug_ = Language("ug", "Q13263")  # Uyghur
        self.ug_arab_ = Language("ug-arab", "Q13263")  # Uyghur (Arabic script)
        self.ug_latn_ = Language("ug-latn", "Q13263")  # Uyghur (Latin script)
        self.uz_ = Language("uz", "Q9264")  # Uzbek
        self.uz_cyrl_ = Language("uz-cyrl", "Q9264")  # Uzbek (Cyrillic script)
        self.uz_latn_ = Language("uz-latn", "Q9264")  # Uzbek (Latin script)
        self.ve_ = Language("ve", "Q32704")  # Venda
        self.vec_ = Language("vec", "Q32724")  # Venetian
        self.vls_ = Language("vls", "Q100103")  # West Flemish
        self.vot_ = Language("vot", "Q32858")  # Votic
        self.vro_ = Language("vro", "Q32762")  # Võro
        self.vut_ = Language("vut", "Q36897")  # Vute
        self.war_ = Language("war", "Q34279")  # Waray
        self.wes_ = Language("wes", "Q35541")  # Pidgin (Cameroon)
        self.wls_ = Language("wls", "Q36979")  # Wallisian
        self.wo_ = Language("wo", "Q34257")  # Wolof
        self.wuu_ = Language("wuu", "Q34290")  # Wu Chinese
        self.wya_ = Language("wya", "Q1185119")  # Wyandot
        self.xal_ = Language("xal", "Q33634")  # Kalmyk
        self.xh_ = Language("xh", "Q13218")  # Xhosa
        self.xmf_ = Language("xmf", "Q13359")  # Mingrelian
        self.xsy_ = Language("xsy", "Q716695")  # Saisiyat
        self.yas_ = Language("yas", "Q36358")  # Nugunu
        self.yat_ = Language("yat", "Q8048020")  # Yambeta
        self.yav_ = Language("yav", "Q12953315")  # Yangben
        self.ybb_ = Language("ybb", "Q36917")  # Yemba
        self.yi_ = Language("yi", "Q8641")  # Yiddish
        self.yo_ = Language("yo", "Q34311")  # Yoruba
        self.yrl_ = Language("yrl", "Q34333")  # Nheengatu
        self.yue_ = Language("yue", "Q7033959")  # Cantonese
        self.za_ = Language("za", "Q13216")  # Zhuang
        self.zea_ = Language("zea", "Q237409")  # Zeelandic
        self.zgh_ = Language("zgh", "Q7598268")  # Standard Moroccan Tamazight
        self.zu_ = Language("zu", "Q10179")  # Zulu

        self.bangali_ = Language("bn-x-Q48726740", "Q48726740") # bangali
        self.varendri_ = Language("bn-x-Q48726757", "Q48726757") # varendri
        self.manbhumi_ = Language("bn-x-Q6747180", "Q6747180") # manbhumi
        self.rarhi_ = Language("bn-x-Q48726759", "Q48726759") # rarhi
        self.noakhailla_ = Language("bn-x-Q107548681", "Q107548681") # noakhailla

langs: Languages = Languages()

def get_first_lang(arg: str) -> Language:
    """ Obtains the first language in tfsl.langs with the given language code. """
    try:
        return langs.find(arg)[0]
    except IndexError as e:
        raise Exception('Could not find', arg) from e
