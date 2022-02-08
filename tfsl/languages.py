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
langs.ba_ = Language("ba", "Q13389")  # Bashkir
langs.bar_ = Language("bar", "Q29540")  # Bavarian
langs.be_ = Language("be", "Q9091")  # Belarusian
langs.be_tarask_ = Language("be-tarask", "Q9091")  # Taraskievica
langs.br_ = Language("br", "Q12107")  # Breton
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
langs.fy_ = Language("fy", "Q27175")  # West Frisian
langs.gd_ = Language("gd", "Q9314")  # Scottish Gaelic
langs.gl_ = Language("gl", "Q9307")  # Galician
langs.gn_ = Language("gn", "Q35876")  # Guarani
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
langs.kw_ = Language("kw", "Q25289")  # Cornish
langs.la_ = Language("la", "Q397")  # Latin
langs.lb_ = Language("lb", "Q9051")  # Luxembourgish
langs.lfn_ = Language("lfn", "Q146803")  # Lingua Franca Nova
langs.mk_ = Language("mk", "Q9296")  # Macedonian
langs.ms_ = Language("ms", "Q9237")  # Malay
langs.ms_arab_ = Language("ms-arab", "Q9237")  # Malay (Jawi)
langs.myv_ = Language("myv", "Q29952")  # Erzya
langs.nan_ = Language("nan", "Q36495")  # Southern Min
langs.nqo_ = Language("nqo", "Q35772")  # Manding languages
langs.oc_ = Language("oc", "Q14185")  # Occitan
langs.olo_ = Language("olo", "Q36584")  # Livvi-Karelian
langs.pi_ = Language("pi", "Q36727")  # Pali
langs.ps_ = Language("ps", "Q58680")  # Pashto
langs.pt_br_ = Language("pt-br", "Q750553")  # Brazilian Portuguese
langs.pwn_ = Language("pwn", "Q715755")  # Paiwan
langs.rm_ = Language("rm", "Q13199")  # Romansh
langs.scn_ = Language("scn", "Q33973")  # Sicilian
langs.sco_ = Language("sco", "Q14549")  # Scots
langs.sq_ = Language("sq", "Q8748")  # Albanian
langs.ss_ = Language("ss", "Q34014")  # Swazi
langs.tg_ = Language("tg", "Q9260")  # Tajik
langs.th_ = Language("th", "Q9217")  # Thai
langs.tr_ = Language("tr", "Q256")  # Turkish
langs.tw_ = Language("tw", "Q36850")  # Twi
langs.udm_ = Language("udm", "Q13238")  # Udmurt
langs.uk_ = Language("uk", "Q8798")  # Ukrainian
langs.vep_ = Language("vep", "Q32747")  # Veps
langs.vi_ = Language("vi", "Q9199")  # Vietnamese
langs.vmf_ = Language("vmf", "Q71223")  # East Franconian
langs.vo_ = Language("vo", "Q36986")  # Volapuk
langs.wa_ = Language("wa", "Q34219")  # Walloon
langs.zxx_ = Language("zxx", "Q22282939")  # no linguistic content
langs.mis_ = Language("mis", "Q22283016")  # language without a specific language code

# languages that should be deleted from Wikimedia projects soon
langs.no_ = Language("no", "Q9043")  # Norwegian
# Lahjas and Darjas
langs.arq_ = Language("arq", "Q56499")  # Algerian
langs.ary_ = Language("ary", "Q56426")  # Moroccan
langs.arz_ = Language("arz", "Q29919")  # Egyptian
# Shtokavian variants
langs.bs_ = Language("bs", "Q9303")  # Bosnian
langs.hr_ = Language("hr", "Q6654")  # Croatian
langs.sr_ = Language("sr", "Q9299")  # Serbian
langs.sr_ec_ = Language("sr-ec", "Q9299")  # Serbian written in Cyrillic
# certain languages of Southeast Asia
langs.id_ = Language("id", "Q9240")  # Indonesian
# certain languages of East Asia
langs.zh_cn_ = Language("zh-cn", "Q9192")  # Mandarin (Mainland)
langs.zh_hans_ = Language("zh-hans", "Q9192")  # Mandarin (Simplified)
langs.zh_hant_ = Language("zh-hant", "Q9192")  # Mandarin (Traditional)
langs.zh_hk_ = Language("zh-hk", "Q9192")  # Chinese (Hong Kong)
langs.zh_mo_ = Language("zh-mo", "Q9192")  # Chinese (Macau)
langs.zh_my_ = Language("zh-my", "Q9192")  # Chinese (Malaysia)
langs.zh_sg_ = Language("zh-sg", "Q9192")  # Chinese (Singapore)
langs.zh_tw_ = Language("zh-tw", "Q9192")  # Mandarin (Taiwan)

# TODO: clean up the giant mess below, imported from the label languages list
langs.aa_ = Language("aa", "Q27811")  # Afar
langs.ab_ = Language("ab", "Q5111")  # Abkhazian
langs.abs_ = Language("abs", "Q3124354")  # Ambonese Malay
langs.ace_ = Language("ace", "Q27683")  # Achinese
langs.ady_ = Language("ady", "Q27776")  # Adyghe
langs.ady_cyrl_ = Language("ady-cyrl", "Q27776")  # Adyghe (Cyrillic script)
langs.aeb_ = Language("aeb", "Q56240")  # Tunisian Arabic
langs.aeb_arab_ = Language("aeb-arab", "Q56240")  # Tunisian Arabic (Arabic script)
langs.aeb_latn_ = Language("aeb-latn", "Q56240")  # Tunisian Arabic (Latin script)
langs.agq_ = Language("agq", "Aghem")  # Aghem
langs.ak_ = Language("ak", "Akan")  # Akan
langs.aln_ = Language("aln", "Gheg Albanian")  # Gheg Albanian
langs.als_ = Language("als", "Alemannisch")  # Alemannisch
langs.alt_ = Language("alt", "Southern Altai")  # Southern Altai
langs.am_ = Language("am", "Amharic")  # Amharic
langs.ami_ = Language("ami", "Amis")  # Amis
langs.an_ = Language("an", "Aragonese")  # Aragonese
langs.ang_ = Language("ang", "Old English")  # Old English
langs.anp_ = Language("anp", "Angika")  # Angika
langs.arc_ = Language("arc", "Aramaic")  # Aramaic
langs.arn_ = Language("arn", "Mapuche")  # Mapuche
langs.ase_ = Language("ase", "American Sign Language")  # American Sign Language
langs.atj_ = Language("atj", "Atikamekw")  # Atikamekw
langs.av_ = Language("av", "Avaric")  # Avaric
langs.avk_ = Language("avk", "Kotava")  # Kotava
langs.awa_ = Language("awa", "Awadhi")  # Awadhi
langs.ay_ = Language("ay", "Aymara")  # Aymara
langs.azb_ = Language("azb", "South Azerbaijani")  # South Azerbaijani
langs.bag_ = Language("bag", "Tuki")  # Tuki
langs.ban_ = Language("ban", "Balinese")  # Balinese
langs.ban_bali_ = Language("ban-bali", "ᬩᬲᬩᬮᬶ")  # ᬩᬲᬩᬮᬶ
langs.bas_ = Language("bas", "Basaa")  # Basaa
langs.bat_smg_ = Language("bat-smg", "Samogitian")  # Samogitian
langs.bax_ = Language("bax", "Bamun")  # Bamun
langs.bbc_ = Language("bbc", "Batak Toba")  # Batak Toba
langs.bbc_latn_ = Language("bbc-latn", "Batak Toba (Latin script)")  # Batak Toba (Latin script)
langs.bbj_ = Language("bbj", "Ghomala")  # Ghomala
langs.bcc_ = Language("bcc", "Southern Balochi")  # Southern Balochi
langs.bcl_ = Language("bcl", "Central Bikol")  # Central Bikol
langs.be_x_old_ = Language("be-x-old", "Q9091")  # Belarusian (Taraškievica orthography)
langs.bgn_ = Language("bgn", "Western Balochi")  # Western Balochi
langs.bh_ = Language("bh", "Bhojpuri")  # Bhojpuri
langs.bi_ = Language("bi", "Bislama")  # Bislama
langs.bjn_ = Language("bjn", "Banjar")  # Banjar
langs.bkc_ = Language("bkc", "Baka")  # Baka
langs.bkh_ = Language("bkh", "Bakako")  # Bakako
langs.bkm_ = Language("bkm", "Kom")  # Kom
langs.bm_ = Language("bm", "Bambara")  # Bambara
langs.bo_ = Language("bo", "Tibetan")  # Tibetan
langs.bpy_ = Language("bpy", "Bishnupriya")  # Bishnupriya
langs.bqi_ = Language("bqi", "Bakhtiari")  # Bakhtiari
langs.brh_ = Language("brh", "Brahui")  # Brahui
langs.btm_ = Language("btm", "Batak Mandailing")  # Batak Mandailing
langs.bto_ = Language("bto", "Iriga Bicolano")  # Iriga Bicolano
langs.bug_ = Language("bug", "Buginese")  # Buginese
langs.bxr_ = Language("bxr", "Russia Buriat")  # Russia Buriat
langs.byv_ = Language("byv", "Medumba")  # Medumba
langs.cak_ = Language("cak", "Kaqchikel")  # Kaqchikel
langs.cbk_zam_ = Language("cbk-zam", "Chavacano")  # Chavacano
langs.cdo_ = Language("cdo", "Min Dong Chinese")  # Min Dong Chinese
langs.ce_ = Language("ce", "Chechen")  # Chechen
langs.ceb_ = Language("ceb", "Cebuano")  # Cebuano
langs.ch_ = Language("ch", "Chamorro")  # Chamorro
langs.cho_ = Language("cho", "Choctaw")  # Choctaw
langs.chr_ = Language("chr", "Cherokee")  # Cherokee
langs.chy_ = Language("chy", "Cheyenne")  # Cheyenne
langs.ckb_ = Language("ckb", "Central Kurdish")  # Central Kurdish
langs.co_ = Language("co", "Corsican")  # Corsican
langs.cps_ = Language("cps", "Capiznon")  # Capiznon
langs.cr_ = Language("cr", "Cree")  # Cree
langs.crh_ = Language("crh", "Q33357")  # Crimean Tatar
langs.crh_cyrl_ = Language("crh-cyrl", "Q33357")  # Crimean Tatar (Cyrillic script)
langs.crh_latn_ = Language("crh-latn", "Q33357")  # Crimean Tatar (Latin script)
langs.csb_ = Language("csb", "Kashubian")  # Kashubian
langs.cu_ = Language("cu", "Church Slavic")  # Church Slavic
langs.cv_ = Language("cv", "Chuvash")  # Chuvash
langs.de_formal_ = Language("de-formal", "German (formal address)")  # German (formal address)
langs.din_ = Language("din", "Dinka")  # Dinka
langs.diq_ = Language("diq", "Zazaki")  # Zazaki
langs.dtp_ = Language("dtp", "Central Dusun")  # Central Dusun
langs.dty_ = Language("dty", "Doteli")  # Doteli
langs.dua_ = Language("dua", "Duala")  # Duala
langs.dv_ = Language("dv", "Divehi")  # Divehi
langs.dz_ = Language("dz", "Dzongkha")  # Dzongkha
langs.ee_ = Language("ee", "Ewe")  # Ewe
langs.egl_ = Language("egl", "Emilian")  # Emilian
langs.eml_ = Language("eml", "Emiliano-Romagnolo")  # Emiliano-Romagnolo
langs.en_ca_ = Language("en-ca", "Canadian English")  # Canadian English
langs.en_us_ = Language("en-us", "American English")  # American English
langs.es_419_ = Language("es-419", "Latin American Spanish")  # Latin American Spanish
langs.es_formal_ = Language("es-formal", "Spanish (formal address)")  # Spanish (formal address)
langs.eto_ = Language("eto", "Eton")  # Eton
langs.etu_ = Language("etu", "Ejagham")  # Ejagham
langs.ewo_ = Language("ewo", "Ewondo")  # Ewondo
langs.ext_ = Language("ext", "Extremaduran")  # Extremaduran
langs.ff_ = Language("ff", "Fulah")  # Fulah
langs.fit_ = Language("fit", "Tornedalen Finnish")  # Tornedalen Finnish
langs.fj_ = Language("fj", "Fijian")  # Fijian
langs.fkv_ = Language("fkv", "Kvensk")  # Kvensk
langs.fmp_ = Language("fmp", "Fe'Fe'")  # Fe'Fe'
langs.fon_ = Language("fon", "Fon")  # Fon
langs.frc_ = Language("frc", "Cajun French")  # Cajun French
langs.frp_ = Language("frp", "Arpitan")  # Arpitan
langs.frr_ = Language("frr", "Northern Frisian")  # Northern Frisian
langs.fur_ = Language("fur", "Friulian")  # Friulian
langs.gag_ = Language("gag", "Gagauz")  # Gagauz
langs.gan_ = Language("gan", "Q33475")  # Gan Chinese
langs.gan_hans_ = Language("gan-hans", "Q33475")  # Gan (Simplified)
langs.gan_hant_ = Language("gan-hant", "Q33475")  # Gan (Traditional)
langs.gcr_ = Language("gcr", "Guianan Creole")  # Guianan Creole
langs.glk_ = Language("glk", "Gilaki")  # Gilaki
langs.gom_ = Language("gom", "Goan Konkani")  # Goan Konkani
langs.gor_ = Language("gor", "Gorontalo")  # Gorontalo
langs.got_ = Language("got", "Gothic")  # Gothic
langs.grc_ = Language("grc", "Ancient Greek")  # Ancient Greek
langs.gsw_ = Language("gsw", "Swiss German")  # Swiss German
langs.guc_ = Language("guc", "Wayuu")  # Wayuu
langs.gur_ = Language("gur", "Frafra")  # Frafra
langs.guw_ = Language("guw", "Gun")  # Gun
langs.gv_ = Language("gv", "Manx")  # Manx
langs.gya_ = Language("gya", "Gbaya")  # Gbaya
langs.hak_ = Language("hak", "Hakka Chinese")  # Hakka Chinese
langs.haw_ = Language("haw", "Hawaiian")  # Hawaiian
langs.hif_ = Language("hif", "Fiji Hindi")  # Fiji Hindi
langs.hif_latn_ = Language("hif-latn", "Fiji Hindi (Latin script)")  # Fiji Hindi (Latin script)
langs.hil_ = Language("hil", "Hiligaynon")  # Hiligaynon
langs.ho_ = Language("ho", "Hiri Motu")  # Hiri Motu
langs.hrx_ = Language("hrx", "Hunsrik")  # Hunsrik
langs.ht_ = Language("ht", "Haitian Creole")  # Haitian Creole
langs.hu_formal_ = Language("hu-formal", "Hungarian (formal address)")  # Hungarian (formal address)
langs.hyw_ = Language("hyw", "Western Armenian")  # Western Armenian
langs.hz_ = Language("hz", "Herero")  # Herero
langs.ia_ = Language("ia", "Interlingua")  # Interlingua
langs.ie_ = Language("ie", "Interlingue")  # Interlingue
langs.ii_ = Language("ii", "Sichuan Yi")  # Sichuan Yi
langs.ik_ = Language("ik", "Inupiaq")  # Inupiaq
langs.ike_cans_ = Language("ike-cans", "Eastern Canadian (Aboriginal syllabics)")  # Eastern Canadian (Aboriginal syllabics)
langs.ike_latn_ = Language("ike-latn", "Eastern Canadian (Latin script)")  # Eastern Canadian (Latin script)
langs.ilo_ = Language("ilo", "Iloko")  # Iloko
langs.inh_ = Language("inh", "Ingush")  # Ingush
langs.isu_ = Language("isu", "Isu")  # Isu
langs.iu_ = Language("iu", "Inuktitut")  # Inuktitut
langs.jam_ = Language("jam", "Jamaican Creole English")  # Jamaican Creole English
langs.jbo_ = Language("jbo", "Lojban")  # Lojban
langs.jut_ = Language("jut", "Jutish")  # Jutish
langs.kaa_ = Language("kaa", "Kara-Kalpak")  # Kara-Kalpak
langs.kab_ = Language("kab", "Kabyle")  # Kabyle
langs.kbd_ = Language("kbd", "Kabardian")  # Kabardian
langs.kbd_cyrl_ = Language("kbd-cyrl", "Kabardian (Cyrillic script)")  # Kabardian (Cyrillic script)
langs.kbp_ = Language("kbp", "Kabiye")  # Kabiye
langs.kcg_ = Language("kcg", "Tyap")  # Tyap
langs.kea_ = Language("kea", "Kabuverdianu")  # Kabuverdianu
langs.ker_ = Language("ker", "Kera")  # Kera
langs.kg_ = Language("kg", "Kongo")  # Kongo
langs.khw_ = Language("khw", "Khowar")  # Khowar
langs.ki_ = Language("ki", "Kikuyu")  # Kikuyu
langs.kiu_ = Language("kiu", "Kirmanjki")  # Kirmanjki
langs.kj_ = Language("kj", "Kuanyama")  # Kuanyama
langs.kjp_ = Language("kjp", "Eastern Pwo")  # Eastern Pwo
langs.kk_arab_ = Language("kk-arab", "Q9252")  # Kazakh (Arabic script)
langs.kk_cn_ = Language("kk-cn", "Q9252")  # Kazakh (China)
langs.kk_cyrl_ = Language("kk-cyrl", "Q9252")  # Kazakh (Cyrillic script)
langs.kk_kz_ = Language("kk-kz", "Q9252")  # Kazakh (Kazakhstan)
langs.kk_latn_ = Language("kk-latn", "Q9252")  # Kazakh (Latin script)
langs.kk_tr_ = Language("kk-tr", "Kazakh (Turkey)")  # Kazakh (Turkey)
langs.km_ = Language("km", "Khmer")  # Khmer
langs.ko_kp_ = Language("ko-kp", "Korean (North Korea)")  # Korean (North Korea)
langs.koi_ = Language("koi", "Komi-Permyak")  # Komi-Permyak
langs.kr_ = Language("kr", "Kanuri")  # Kanuri
langs.krc_ = Language("krc", "Karachay-Balkar")  # Karachay-Balkar
langs.kri_ = Language("kri", "Krio")  # Krio
langs.krj_ = Language("krj", "Kinaray-a")  # Kinaray-a
langs.krl_ = Language("krl", "Karelian")  # Karelian
langs.ks_ = Language("ks", "Kashmiri")  # Kashmiri
langs.ksf_ = Language("ksf", "Bafia")  # Bafia
langs.ksh_ = Language("ksh", "Colognian")  # Colognian
langs.ku_ = Language("ku", "Q36163")  # Kurdish
langs.ku_arab_ = Language("ku-arab", "Q36163")  # Kurdish (Arabic script)
langs.ku_latn_ = Language("ku-latn", "Q36163")  # Kurdish (Latin script)
langs.kum_ = Language("kum", "Kumyk")  # Kumyk
langs.kv_ = Language("kv", "Komi")  # Komi
langs.ky_ = Language("ky", "Kyrgyz")  # Kyrgyz
langs.lad_ = Language("lad", "Ladino")  # Ladino
langs.lbe_ = Language("lbe", "Lak")  # Lak
langs.lem_ = Language("lem", "Nomaande")  # Nomaande
langs.lez_ = Language("lez", "Lezghian")  # Lezghian
langs.lg_ = Language("lg", "Ganda")  # Ganda
langs.li_ = Language("li", "Limburgish")  # Limburgish
langs.lij_ = Language("lij", "Ligurian")  # Ligurian
langs.liv_ = Language("liv", "Livonian")  # Livonian
langs.lki_ = Language("lki", "Laki")  # Laki
langs.lld_ = Language("lld", "Ladin")  # Ladin
langs.lmo_ = Language("lmo", "Lombard")  # Lombard
langs.ln_ = Language("ln", "Lingala")  # Lingala
langs.lns_ = Language("lns", "Lamnso'")  # Lamnso'
langs.lo_ = Language("lo", "Lao")  # Lao
langs.loz_ = Language("loz", "Lozi")  # Lozi
langs.lrc_ = Language("lrc", "Northern Luri")  # Northern Luri
langs.ltg_ = Language("ltg", "Latgalian")  # Latgalian
langs.lus_ = Language("lus", "Mizo")  # Mizo
langs.luz_ = Language("luz", "Southern Luri")  # Southern Luri
langs.lzh_ = Language("lzh", "Literary Chinese")  # Literary Chinese
langs.lzz_ = Language("lzz", "Laz")  # Laz
langs.mad_ = Language("mad", "Madurese")  # Madurese
langs.map_bms_ = Language("map-bms", "Basa Banyumasan")  # Basa Banyumasan
langs.mcn_ = Language("mcn", "Massa")  # Massa
langs.mcp_ = Language("mcp", "Maka")  # Maka
langs.mdf_ = Language("mdf", "Moksha")  # Moksha
langs.mg_ = Language("mg", "Malagasy")  # Malagasy
langs.mh_ = Language("mh", "Marshallese")  # Marshallese
langs.mhr_ = Language("mhr", "Eastern Mari")  # Eastern Mari
langs.mi_ = Language("mi", "Maori")  # Maori
langs.min_ = Language("min", "Minangkabau")  # Minangkabau
langs.mn_ = Language("mn", "Mongolian")  # Mongolian
langs.mnw_ = Language("mnw", "Mon")  # Mon
langs.mo_ = Language("mo", "Moldovan")  # Moldovan
langs.mrh_ = Language("mrh", "Mara")  # Mara
langs.mrj_ = Language("mrj", "Western Mari")  # Western Mari
langs.mua_ = Language("mua", "Mundang")  # Mundang
langs.mus_ = Language("mus", "Muscogee")  # Muscogee
langs.mwl_ = Language("mwl", "Mirandese")  # Mirandese
langs.my_ = Language("my", "Burmese")  # Burmese
langs.mzn_ = Language("mzn", "Mazanderani")  # Mazanderani
langs.na_ = Language("na", "Nauru")  # Nauru
langs.nah_ = Language("nah", "Nāhuatl")  # Nāhuatl
langs.nan_hani_ = Language("nan-hani", "Min Nan (Hanji)")  # Min Nan (Hanji)
langs.nap_ = Language("nap", "Neapolitan")  # Neapolitan
langs.nds_ = Language("nds", "Low German")  # Low German
langs.nds_nl_ = Language("nds-nl", "Low Saxon")  # Low Saxon
langs.new_ = Language("new", "Newari")  # Newari
langs.ng_ = Language("ng", "Ndonga")  # Ndonga
langs.nia_ = Language("nia", "Nias")  # Nias
langs.niu_ = Language("niu", "Niuean")  # Niuean
langs.nl_informal_ = Language("nl-informal", "Dutch (informal address)")  # Dutch (informal address)
langs.nla_ = Language("nla", "Ngombala")  # Ngombala
langs.nmg_ = Language("nmg", "Kwasio")  # Kwasio
langs.nnh_ = Language("nnh", "Ngiemboon")  # Ngiemboon
langs.nod_ = Language("nod", "Northern Thai")  # Northern Thai
langs.nov_ = Language("nov", "Novial")  # Novial
langs.nrm_ = Language("nrm", "Norman")  # Norman
langs.nso_ = Language("nso", "Northern Sotho")  # Northern Sotho
langs.nv_ = Language("nv", "Navajo")  # Navajo
langs.ny_ = Language("ny", "Nyanja")  # Nyanja
langs.nys_ = Language("nys", "Nyungar")  # Nyungar
langs.ojb_ = Language("ojb", "Northwestern Ojibwe")  # Northwestern Ojibwe
langs.om_ = Language("om", "Oromo")  # Oromo
langs.os_ = Language("os", "Ossetic")  # Ossetic
langs.osa_latn_ = Language("osa-latn", "Osage (Latin script)")  # Osage (Latin script)
langs.ota_ = Language("ota", "Ottoman Turkish")  # Ottoman Turkish
langs.pag_ = Language("pag", "Pangasinan")  # Pangasinan
langs.pam_ = Language("pam", "Pampanga")  # Pampanga
langs.pap_ = Language("pap", "Papiamento")  # Papiamento
langs.pcd_ = Language("pcd", "Picard")  # Picard
langs.pdc_ = Language("pdc", "Pennsylvania German")  # Pennsylvania German
langs.pdt_ = Language("pdt", "Plautdietsch")  # Plautdietsch
langs.pfl_ = Language("pfl", "Palatine German")  # Palatine German
langs.pih_ = Language("pih", "Norfuk / Pitkern")  # Norfuk / Pitkern
langs.pms_ = Language("pms", "Piedmontese")  # Piedmontese
langs.pnt_ = Language("pnt", "Pontic")  # Pontic
langs.prg_ = Language("prg", "Prussian")  # Prussian
langs.qu_ = Language("qu", "Quechua")  # Quechua
langs.quc_ = Language("quc", "Kʼicheʼ")  # Kʼicheʼ
langs.qug_ = Language("qug", "Chimborazo Highland Quichua")  # Chimborazo Highland Quichua
langs.rgn_ = Language("rgn", "Romagnol")  # Romagnol
langs.rif_ = Language("rif", "Riffian")  # Riffian
langs.rmc_ = Language("rmc", "Carpathian Romani")  # Carpathian Romani
langs.rmf_ = Language("rmf", "Finnish Kalo")  # Finnish Kalo
langs.rmy_ = Language("rmy", "Vlax Romani")  # Vlax Romani
langs.rn_ = Language("rn", "Rundi")  # Rundi
langs.roa_rup_ = Language("roa-rup", "Aromanian")  # Aromanian
langs.roa_tara_ = Language("roa-tara", "Tarantino")  # Tarantino
langs.rue_ = Language("rue", "Rusyn")  # Rusyn
langs.rup_ = Language("rup", "Aromanian")  # Aromanian
langs.ruq_ = Language("ruq", "Q13358")  # Megleno-Romanian
langs.ruq_cyrl_ = Language("ruq-cyrl", "Q13358")  # Megleno-Romanian (Cyrillic script)
langs.ruq_latn_ = Language("ruq-latn", "Q13358")  # Megleno-Romanian (Latin script)
langs.rw_ = Language("rw", "Kinyarwanda")  # Kinyarwanda
langs.rwr_ = Language("rwr", "Marwari (India)")  # Marwari (India)
langs.ryu_ = Language("ryu", "Okinawan")  # Okinawan
langs.sah_ = Language("sah", "Sakha")  # Sakha
langs.sc_ = Language("sc", "Sardinian")  # Sardinian
langs.sdc_ = Language("sdc", "Sassarese Sardinian")  # Sassarese Sardinian
langs.sdh_ = Language("sdh", "Southern Kurdish")  # Southern Kurdish
langs.sei_ = Language("sei", "Seri")  # Seri
langs.ses_ = Language("ses", "Koyraboro Senni")  # Koyraboro Senni
langs.sg_ = Language("sg", "Sango")  # Sango
langs.sgs_ = Language("sgs", "Samogitian")  # Samogitian
langs.sh_ = Language("sh", "Serbo-Croatian")  # Serbo-Croatian
langs.shi_ = Language("shi", "Q34152")  # Tachelhit
langs.shi_latn_ = Language("shi-latn", "Q34152")  # Tachelhit (Latin script)
langs.shi_tfng_ = Language("shi-tfng", "Q34152")  # Tachelhit (Tifinagh script)
langs.shn_ = Language("shn", "Shan")  # Shan
langs.shy_ = Language("shy", "Shawiya")  # Shawiya
langs.shy_latn_ = Language("shy-latn", "Shawiya (Latin script)")  # Shawiya (Latin script)
langs.si_ = Language("si", "Sinhala")  # Sinhala
langs.simple_ = Language("simple", "Simple English")  # Simple English
langs.skr_ = Language("skr", "Saraiki")  # Saraiki
langs.skr_arab_ = Language("skr-arab", "Saraiki (Arabic script)")  # Saraiki (Arabic script)
langs.sli_ = Language("sli", "Lower Silesian")  # Lower Silesian
langs.sm_ = Language("sm", "Samoan")  # Samoan
langs.sn_ = Language("sn", "Shona")  # Shona
langs.so_ = Language("so", "Somali")  # Somali
langs.sr_el_ = Language("sr-el", "Serbian (Latin script)")  # Serbian (Latin script)
langs.srn_ = Language("srn", "Sranan Tongo")  # Sranan Tongo
langs.srq_ = Language("srq", "Sirionó")  # Sirionó
langs.st_ = Language("st", "Southern Sotho")  # Southern Sotho
langs.stq_ = Language("stq", "Saterland Frisian")  # Saterland Frisian
langs.sty_ = Language("sty", "Siberian Tatar")  # Siberian Tatar
langs.su_ = Language("su", "Sundanese")  # Sundanese
langs.sw_ = Language("sw", "Swahili")  # Swahili
langs.szl_ = Language("szl", "Silesian")  # Silesian
langs.szy_ = Language("szy", "Sakizaya")  # Sakizaya
langs.tay_ = Language("tay", "Tayal")  # Tayal
langs.tcy_ = Language("tcy", "Tulu")  # Tulu
langs.tet_ = Language("tet", "Tetum")  # Tetum
langs.tg_cyrl_ = Language("tg-cyrl", "Tajik (Cyrillic script)")  # Tajik (Cyrillic script)
langs.tg_latn_ = Language("tg-latn", "Tajik (Latin script)")  # Tajik (Latin script)
langs.ti_ = Language("ti", "Tigrinya")  # Tigrinya
langs.tk_ = Language("tk", "Turkmen")  # Turkmen
langs.tl_ = Language("tl", "Tagalog")  # Tagalog
langs.tly_ = Language("tly", "Talysh")  # Talysh
langs.tly_cyrl_ = Language("tly-cyrl", "толыши")  # толыши
langs.tn_ = Language("tn", "Tswana")  # Tswana
langs.to_ = Language("to", "Tongan")  # Tongan
langs.tpi_ = Language("tpi", "Tok Pisin")  # Tok Pisin
langs.tru_ = Language("tru", "Turoyo")  # Turoyo
langs.trv_ = Language("trv", "Taroko")  # Taroko
langs.ts_ = Language("ts", "Tsonga")  # Tsonga
langs.tt_ = Language("tt", "Tatar")  # Tatar
langs.tt_cyrl_ = Language("tt-cyrl", "Tatar (Cyrillic script)")  # Tatar (Cyrillic script)
langs.tt_latn_ = Language("tt-latn", "Tatar (Latin script)")  # Tatar (Latin script)
langs.tum_ = Language("tum", "Tumbuka")  # Tumbuka
langs.tvu_ = Language("tvu", "Tunen")  # Tunen
langs.ty_ = Language("ty", "Tahitian")  # Tahitian
langs.tyv_ = Language("tyv", "Tuvinian")  # Tuvinian
langs.tzm_ = Language("tzm", "Central Atlas Tamazight")  # Central Atlas Tamazight
langs.ug_ = Language("ug", "Q13263")  # Uyghur
langs.ug_arab_ = Language("ug-arab", "Q13263")  # Uyghur (Arabic script)
langs.ug_latn_ = Language("ug-latn", "Q13263")  # Uyghur (Latin script)
langs.uz_ = Language("uz", "Q9264")  # Uzbek
langs.uz_cyrl_ = Language("uz-cyrl", "Q9264")  # Uzbek (Cyrillic script)
langs.uz_latn_ = Language("uz-latn", "Q9264")  # Uzbek (Latin script)
langs.ve_ = Language("ve", "Venda")  # Venda
langs.vec_ = Language("vec", "Venetian")  # Venetian
langs.vls_ = Language("vls", "West Flemish")  # West Flemish
langs.vot_ = Language("vot", "Votic")  # Votic
langs.vro_ = Language("vro", "Võro")  # Võro
langs.vut_ = Language("vut", "Vute")  # Vute
langs.war_ = Language("war", "Waray")  # Waray
langs.wes_ = Language("wes", "Pidgin (Cameroon)")  # Pidgin (Cameroon)
langs.wls_ = Language("wls", "Wallisian")  # Wallisian
langs.wo_ = Language("wo", "Wolof")  # Wolof
langs.wuu_ = Language("wuu", "Wu Chinese")  # Wu Chinese
langs.wya_ = Language("wya", "Wyandot")  # Wyandot
langs.xal_ = Language("xal", "Kalmyk")  # Kalmyk
langs.xh_ = Language("xh", "Xhosa")  # Xhosa
langs.xmf_ = Language("xmf", "Mingrelian")  # Mingrelian
langs.xsy_ = Language("xsy", "Saisiyat")  # Saisiyat
langs.yas_ = Language("yas", "Nugunu")  # Nugunu
langs.yat_ = Language("yat", "Yambeta")  # Yambeta
langs.yav_ = Language("yav", "Yangben")  # Yangben
langs.ybb_ = Language("ybb", "Yemba")  # Yemba
langs.yi_ = Language("yi", "Yiddish")  # Yiddish
langs.yo_ = Language("yo", "Yoruba")  # Yoruba
langs.yrl_ = Language("yrl", "Nheengatu")  # Nheengatu
langs.yue_ = Language("yue", "Cantonese")  # Cantonese
langs.za_ = Language("za", "Zhuang")  # Zhuang
langs.zea_ = Language("zea", "Zeelandic")  # Zeelandic
langs.zgh_ = Language("zgh", "Standard Moroccan Tamazight")  # Standard Moroccan Tamazight
langs.zh_classical_ = Language("zh-classical", "Classical Chinese")  # Classical Chinese
langs.zh_min_nan_ = Language("zh-min-nan", "Chinese (Min Nan)")  # Chinese (Min Nan)
langs.zh_yue_ = Language("zh-yue", "Cantonese")  # Cantonese
langs.zu_ = Language("zu", "Zulu")  # Zulu
