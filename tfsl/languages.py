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
langs.agq_ = Language("agq", "Q34737")  # Aghem
langs.ak_ = Language("ak", "Q28026")  # Akan
langs.aln_ = Language("aln", "Q181037")  # Gheg Albanian
langs.als_ = Language("als", "Q131339")  # Alemannisch
langs.alt_ = Language("alt", "Q1991779")  # Southern Altai
langs.am_ = Language("am", "Q28244")  # Amharic
langs.ami_ = Language("ami", "Q35132")  # Amis
langs.an_ = Language("an", "Q8765")  # Aragonese
langs.ang_ = Language("ang", "Q42365")  # Old English
langs.anp_ = Language("anp", "Q28378")  # Angika
langs.arc_ = Language("arc", "Q28602")  # Aramaic
langs.arn_ = Language("arn", "Q33730")  # Mapuche
langs.ase_ = Language("ase", "Q14759")  # American Sign Language
langs.atj_ = Language("atj", "Q56590")  # Atikamekw
langs.av_ = Language("av", "Q29561")  # Avaric
langs.avk_ = Language("avk", "Q1377116")  # Kotava
langs.awa_ = Language("awa", "Q29579")  # Awadhi
langs.ay_ = Language("ay", "Q4627")  # Aymara
langs.azb_ = Language("azb", "Q9292")  # South Azerbaijani
langs.bag_ = Language("bag", "Q36621")  # Tuki
langs.ban_ = Language("ban", "Q33070")  # Balinese
langs.ban_bali_ = Language("ban-bali", "Q33070")  # ᬩᬲᬩᬮᬶ
langs.bas_ = Language("bas", "Q33093")  # Basaa
langs.bat_smg_ = Language("bat-smg", "Q213434")  # Samogitian
langs.bax_ = Language("bax", "Q35280")  # Bamun
langs.bbc_ = Language("bbc", "Q33017")  # Batak Toba
langs.bbc_latn_ = Language("bbc-latn", "Q33017")  # Batak Toba (Latin script)
langs.bbj_ = Language("bbj", "Q35271")  # Ghomala
langs.bcc_ = Language("bcc", "Q12634001")  # Southern Balochi
langs.bcl_ = Language("bcl", "Q33284")  # Central Bikol
langs.be_x_old_ = Language("be-x-old", "Q9091")  # Belarusian (Taraškievica orthography)
langs.bgn_ = Language("bgn", "Q12645561")  # Western Balochi
langs.bh_ = Language("bh", "Q33268")  # Bhojpuri
langs.bi_ = Language("bi", "Q35452")  # Bislama
langs.bjn_ = Language("bjn", "Q33151")  # Banjar
langs.bkc_ = Language("bkc", "Q34905")  # Baka
langs.bkh_ = Language("bkh", "Q34866")  # Bakako
langs.bkm_ = Language("bkm", "Q1656595")  # Kom
langs.bm_ = Language("bm", "Q33243")  # Bambara
langs.bo_ = Language("bo", "Q34271")  # Tibetan
langs.bpy_ = Language("bpy", "Q37059")  # Bishnupriya
langs.bqi_ = Language("bqi", "Q257829")  # Bakhtiari
langs.brh_ = Language("brh", "Q33202")  # Brahui
langs.btm_ = Language("btm", "Q2891049")  # Batak Mandailing
langs.bto_ = Language("bto", "Q12633026")  # Iriga Bicolano
langs.bug_ = Language("bug", "Q33190")  # Buginese
langs.bxr_ = Language("bxr", "Q16116629")  # Russia Buriat
langs.byv_ = Language("byv", "Q36019")  # Medumba
langs.cak_ = Language("cak", "Q35115")  # Kaqchikel
langs.cbk_zam_ = Language("cbk-zam", "Q33281")  # Chavacano
langs.cdo_ = Language("cdo", "Q36455")  # Min Dong Chinese
langs.ce_ = Language("ce", "Q33350")  # Chechen
langs.ceb_ = Language("ceb", "Q33239")  # Cebuano
langs.ch_ = Language("ch", "Q33262")  # Chamorro
langs.cho_ = Language("cho", "Q32979")  # Choctaw
langs.chr_ = Language("chr", "Q33388")  # Cherokee
langs.chy_ = Language("chy", "Q33265")  # Cheyenne
langs.ckb_ = Language("ckb", "Q36811")  # Central Kurdish
langs.co_ = Language("co", "Q33111")  # Corsican
langs.cps_ = Language("cps", "Q2937525")  # Capiznon
langs.cr_ = Language("cr", "Q33390")  # Cree
langs.crh_ = Language("crh", "Q33357")  # Crimean Tatar
langs.crh_cyrl_ = Language("crh-cyrl", "Q33357")  # Crimean Tatar (Cyrillic script)
langs.crh_latn_ = Language("crh-latn", "Q33357")  # Crimean Tatar (Latin script)
langs.csb_ = Language("csb", "Q33690")  # Kashubian
langs.cu_ = Language("cu", "Q35499")  # Church Slavic
langs.cv_ = Language("cv", "Q33348")  # Chuvash
langs.de_formal_ = Language("de-formal", "Q188")  # German (formal address)
langs.din_ = Language("din", "Q56466")  # Dinka
langs.diq_ = Language("diq", "Q10199")  # Zazaki
langs.dtp_ = Language("dtp", "Q5317225")  # Central Dusun
langs.dty_ = Language("dty", "Q18415595")  # Doteli
langs.dua_ = Language("dua", "Q33013")  # Duala
langs.dv_ = Language("dv", "Q32656")  # Divehi
langs.dz_ = Language("dz", "Q33081")  # Dzongkha
langs.ee_ = Language("ee", "Q30005")  # Ewe
langs.egl_ = Language("egl", "Q1057898")  # Emilian
langs.eml_ = Language("eml", "Q242648")  # Emiliano-Romagnolo
langs.en_ca_ = Language("en-ca", "Q44676")  # Canadian English
langs.en_us_ = Language("en-us", "Q7976")  # American English
langs.es_419_ = Language("es-419", "Q56649449")  # Latin American Spanish
langs.es_formal_ = Language("es-formal", "Q1321")  # Spanish (formal address)
langs.eto_ = Language("eto", "Q35317")  # Eton
langs.etu_ = Language("etu", "Q35296")  # Ejagham
langs.ewo_ = Language("ewo", "Q35459")  # Ewondo
langs.ext_ = Language("ext", "Q30007")  # Extremaduran
langs.ff_ = Language("ff", "Q33454")  # Fulah
langs.fit_ = Language("fit", "Q13357")  # Tornedalen Finnish
langs.fj_ = Language("fj", "Q33295")  # Fijian
langs.fkv_ = Language("fkv", "Q165795")  # Kvensk
langs.fmp_ = Language("fmp", "Q35276")  # Fe'Fe'
langs.fon_ = Language("fon", "Q33291")  # Fon
langs.frc_ = Language("frc", "Q3083213")  # Cajun French
langs.frp_ = Language("frp", "Q15087")  # Arpitan
langs.frr_ = Language("frr", "Q28224")  # Northern Frisian
langs.fur_ = Language("fur", "Q33441")  # Friulian
langs.gag_ = Language("gag", "Q33457")  # Gagauz
langs.gan_ = Language("gan", "Q33475")  # Gan Chinese
langs.gan_hans_ = Language("gan-hans", "Q33475")  # Gan (Simplified)
langs.gan_hant_ = Language("gan-hant", "Q33475")  # Gan (Traditional)
langs.gcr_ = Language("gcr", "Q1363072")  # Guianan Creole
langs.glk_ = Language("glk", "Q33657")  # Gilaki
langs.gom_ = Language("gom", "Q5575236")  # Goan Konkani
langs.gor_ = Language("gor", "Q2501174")  # Gorontalo
langs.got_ = Language("got", "Q35722")  # Gothic
langs.grc_ = Language("grc", "Q35497")  # Ancient Greek
langs.gsw_ = Language("gsw", "Q131339")  # Swiss German
langs.guc_ = Language("guc", "Q891085")  # Wayuu
langs.gur_ = Language("gur", "Q35331")  # Frafra
langs.guw_ = Language("guw", "Q3111668")  # Gun
langs.gv_ = Language("gv", "Q12175")  # Manx
langs.gya_ = Language("gya", "Q36594")  # Gbaya
langs.hak_ = Language("hak", "Q33375")  # Hakka Chinese
langs.haw_ = Language("haw", "Q33569")  # Hawaiian
langs.hif_ = Language("hif", "Q46728")  # Fiji Hindi
langs.hif_latn_ = Language("hif-latn", "Q46728")  # Fiji Hindi (Latin script)
langs.hil_ = Language("hil", "Q35978")  # Hiligaynon
langs.ho_ = Language("ho", "Q33617")  # Hiri Motu
langs.hrx_ = Language("hrx", "Q304049")  # Hunsrik
langs.ht_ = Language("ht", "Q33491")  # Haitian Creole
langs.hu_formal_ = Language("hu-formal", "Q9067")  # Hungarian (formal address)
langs.hyw_ = Language("hyw", "Q180945")  # Western Armenian
langs.hz_ = Language("hz", "Q33315")  # Herero
langs.ia_ = Language("ia", "Q35934")  # Interlingua
langs.ie_ = Language("ie", "Q35850")  # Interlingue
langs.ii_ = Language("ii", "Q34235")  # Sichuan Yi
langs.ik_ = Language("ik", "Q27183")  # Inupiaq
langs.ike_cans_ = Language("ike-cans", "Q29921")  # Eastern Canadian (Aboriginal syllabics)
langs.ike_latn_ = Language("ike-latn", "Q29921")  # Eastern Canadian (Latin script)
langs.ilo_ = Language("ilo", "Q35936")  # Iloko
langs.inh_ = Language("inh", "Q33509")  # Ingush
langs.isu_ = Language("isu", "Q6089423")  # Isu
langs.iu_ = Language("iu", "Q29921")  # Inuktitut
langs.jam_ = Language("jam", "Q35939")  # Jamaican Creole English
langs.jbo_ = Language("jbo", "Q36350")  # Lojban
langs.jut_ = Language("jut", "Q1340322")  # Jutish
langs.kaa_ = Language("kaa", "Q33541")  # Kara-Kalpak
langs.kab_ = Language("kab", "Q35853")  # Kabyle
langs.kbd_ = Language("kbd", "Q33522")  # Kabardian
langs.kbd_cyrl_ = Language("kbd-cyrl", "Q33522")  # Kabardian (Cyrillic script)
langs.kbp_ = Language("kbp", "Q35475")  # Kabiye
langs.kcg_ = Language("kcg", "Q3912765")  # Tyap
langs.kea_ = Language("kea", "Q35963")  # Kabuverdianu
langs.ker_ = Language("ker", "Q56251")  # Kera
langs.kg_ = Language("kg", "Q33702")  # Kongo
langs.khw_ = Language("khw", "Q938216")  # Khowar
langs.ki_ = Language("ki", "Q33587")  # Kikuyu
langs.kiu_ = Language("kiu", "Q6023868")  # Kirmanjki
langs.kj_ = Language("kj", "Q1405077")  # Kuanyama
langs.kjp_ = Language("kjp", "Q5330390")  # Eastern Pwo
langs.kk_arab_ = Language("kk-arab", "Q9252")  # Kazakh (Arabic script)
langs.kk_cn_ = Language("kk-cn", "Q9252")  # Kazakh (China)
langs.kk_cyrl_ = Language("kk-cyrl", "Q9252")  # Kazakh (Cyrillic script)
langs.kk_kz_ = Language("kk-kz", "Q9252")  # Kazakh (Kazakhstan)
langs.kk_latn_ = Language("kk-latn", "Q9252")  # Kazakh (Latin script)
langs.kk_tr_ = Language("kk-tr", "Q9252")  # Kazakh (Turkey)
langs.km_ = Language("km", "Q9205")  # Khmer
langs.ko_kp_ = Language("ko-kp", "Q9176")  # Korean (North Korea)
langs.koi_ = Language("koi", "Q56318")  # Komi-Permyak
langs.kr_ = Language("kr", "Q36094")  # Kanuri
langs.krc_ = Language("krc", "Q33714")  # Karachay-Balkar
langs.kri_ = Language("kri", "Q35744")  # Krio
langs.krj_ = Language("krj", "Q33720")  # Kinaray-a
langs.krl_ = Language("krl", "Q33557")  # Karelian
langs.ks_ = Language("ks", "Q33552")  # Kashmiri
langs.ksf_ = Language("ksf", "Q34930")  # Bafia
langs.ksh_ = Language("ksh", "Q4624")  # Colognian
langs.ku_ = Language("ku", "Q36163")  # Kurdish
langs.ku_arab_ = Language("ku-arab", "Q36163")  # Kurdish (Arabic script)
langs.ku_latn_ = Language("ku-latn", "Q36163")  # Kurdish (Latin script)
langs.kum_ = Language("kum", "Q36209")  # Kumyk
langs.kv_ = Language("kv", "Q36126")  # Komi
langs.ky_ = Language("ky", "Q9255")  # Kyrgyz
langs.lad_ = Language("lad", "Q36196")  # Ladino
langs.lbe_ = Language("lbe", "Q36206")  # Lak
langs.lem_ = Language("lem", "Q13479983")  # Nomaande
langs.lez_ = Language("lez", "Q31746")  # Lezghian
langs.lg_ = Language("lg", "Q33368")  # Ganda
langs.li_ = Language("li", "Q102172")  # Limburgish
langs.lij_ = Language("lij", "Q36106")  # Ligurian
langs.liv_ = Language("liv", "Q33698")  # Livonian
langs.lki_ = Language("lki", "Q56483")  # Laki
langs.lld_ = Language("lld", "Q36202")  # Ladin
langs.lmo_ = Language("lmo", "Q33754")  # Lombard
langs.ln_ = Language("ln", "Q36217")  # Lingala
langs.lns_ = Language("lns", "Q35788")  # Lamnso'
langs.lo_ = Language("lo", "Q9211")  # Lao
langs.loz_ = Language("loz", "Q33628")  # Lozi
langs.lrc_ = Language("lrc", "Q19933293")  # Northern Luri
langs.ltg_ = Language("ltg", "Q36212")  # Latgalian
langs.lus_ = Language("lus", "Q36147")  # Mizo
langs.luz_ = Language("luz", "Q12952748")  # Southern Luri
langs.lzh_ = Language("lzh", "Q37041")  # Literary Chinese
langs.lzz_ = Language("lzz", "Q1160372")  # Laz
langs.mad_ = Language("mad", "Q36213")  # Madurese
langs.map_bms_ = Language("map-bms", "Q33219")  # Basa Banyumasan
langs.mcn_ = Language("mcn", "Q56668")  # Massa
langs.mcp_ = Language("mcp", "Q35803")  # Maka
langs.mdf_ = Language("mdf", "Q13343")  # Moksha
langs.mg_ = Language("mg", "Q7930")  # Malagasy
langs.mh_ = Language("mh", "Q36280")  # Marshallese
langs.mhr_ = Language("mhr", "Q3906614")  # Eastern Mari
langs.mi_ = Language("mi", "Q36451")  # Maori
langs.min_ = Language("min", "Q13324")  # Minangkabau
langs.mn_ = Language("mn", "Q9246")  # Mongolian
langs.mnw_ = Language("mnw", "Q13349")  # Mon
langs.mo_ = Language("mo", "Q7913")  # Moldovan
langs.mrh_ = Language("mrh", "Q4175893")  # Mara
langs.mrj_ = Language("mrj", "Q1776032")  # Western Mari
langs.mua_ = Language("mua", "Q36032")  # Mundang
langs.mus_ = Language("mus", "Q523014")  # Muscogee
langs.mwl_ = Language("mwl", "Q13330")  # Mirandese
langs.my_ = Language("my", "Q9228")  # Burmese
langs.mzn_ = Language("mzn", "Q13356")  # Mazanderani
langs.na_ = Language("na", "Q13307")  # Nauru
langs.nah_ = Language("nah", "Q13300")  # Nāhuatl
langs.nan_hani_ = Language("nan-hani", "Q36495")  # Min Nan (Hanji)
langs.nap_ = Language("nap", "Q33845")  # Neapolitan
langs.nds_ = Language("nds", "Q25433")  # Low German
langs.nds_nl_ = Language("nds-nl", "Q25433")  # Low Saxon
langs.new_ = Language("new", "Q33979")  # Newari
langs.ng_ = Language("ng", "Q33900")  # Ndonga
langs.nia_ = Language("nia", "Q2407831")  # Nias
langs.niu_ = Language("niu", "Q33790")  # Niuean
langs.nl_informal_ = Language("nl-informal", "Q7411")  # Dutch (informal address)
langs.nla_ = Language("nla", "Q36292")  # Ngombala
langs.nmg_ = Language("nmg", "Q34098")  # Kwasio
langs.nnh_ = Language("nnh", "Q36286")  # Ngiemboon
langs.nod_ = Language("nod", "Q565110")  # Northern Thai
langs.nov_ = Language("nov", "Q36738")  # Novial
langs.nrm_ = Language("nrm", "Q33850")  # Norman
langs.nso_ = Language("nso", "Q33890")  # Northern Sotho
langs.nv_ = Language("nv", "Q13310")  # Navajo
langs.ny_ = Language("ny", "Q33273")  # Nyanja
langs.nys_ = Language("nys", "Q7049771")  # Nyungar
langs.ojb_ = Language("ojb", "Q7060356")  # Northwestern Ojibwe
langs.om_ = Language("om", "Q33864")  # Oromo
langs.os_ = Language("os", "Q33968")  # Ossetic
langs.osa_latn_ = Language("osa-latn", "Q2600085")  # Osage (Latin script)
langs.ota_ = Language("ota", "Q36730")  # Ottoman Turkish
langs.pag_ = Language("pag", "Q33879")  # Pangasinan
langs.pam_ = Language("pam", "Q36121")  # Pampanga
langs.pap_ = Language("pap", "Q33856")  # Papiamento
langs.pcd_ = Language("pcd", "Q34024")  # Picard
langs.pdc_ = Language("pdc", "Q22711")  # Pennsylvania German
langs.pdt_ = Language("pdt", "Q1751432")  # Plautdietsch
langs.pfl_ = Language("pfl", "Q23014")  # Palatine German
langs.pih_ = Language("pih", "Q36554")  # Norfuk / Pitkern
langs.pms_ = Language("pms", "Q15085")  # Piedmontese
langs.pnt_ = Language("pnt", "Q36748")  # Pontic
langs.prg_ = Language("prg", "Q35501")  # Prussian
langs.qu_ = Language("qu", "Q5218")  # Quechua
langs.quc_ = Language("quc", "Q36494")  # Kʼicheʼ
langs.qug_ = Language("qug", "Q12953845")  # Chimborazo Highland Quichua
langs.rgn_ = Language("rgn", "Q1641543")  # Romagnol
langs.rif_ = Language("rif", "Q34174")  # Riffian
langs.rmc_ = Language("rmc", "Q5045611")  # Carpathian Romani
langs.rmf_ = Language("rmf", "Q2093214")  # Finnish Kalo
langs.rmy_ = Language("rmy", "Q2669199")  # Vlax Romani
langs.rn_ = Language("rn", "Q33583")  # Rundi
langs.roa_rup_ = Language("roa-rup", "Q29316")  # Aromanian
langs.roa_tara_ = Language("roa-tara", "Q695526")  # Tarantino
langs.rue_ = Language("rue", "Q26245")  # Rusyn
langs.rup_ = Language("rup", "Q29316")  # Aromanian
langs.ruq_ = Language("ruq", "Q13358")  # Megleno-Romanian
langs.ruq_cyrl_ = Language("ruq-cyrl", "Q13358")  # Megleno-Romanian (Cyrillic script)
langs.ruq_latn_ = Language("ruq-latn", "Q13358")  # Megleno-Romanian (Latin script)
langs.rw_ = Language("rw", "Q33573")  # Kinyarwanda
langs.rwr_ = Language("rwr", "Q65455884")  # Marwari (India)
langs.ryu_ = Language("ryu", "Q34233")  # Okinawan
langs.sah_ = Language("sah", "Q34299")  # Sakha
langs.sc_ = Language("sc", "Q33976")  # Sardinian
langs.sdc_ = Language("sdc", "Q845441")  # Sassarese Sardinian
langs.sdh_ = Language("sdh", "Q1496597")  # Southern Kurdish
langs.sei_ = Language("sei", "Q36583")  # Seri
langs.ses_ = Language("ses", "Q35655")  # Koyraboro Senni
langs.sg_ = Language("sg", "Q33954")  # Sango
langs.sgs_ = Language("sgs", "Q213434")  # Samogitian
langs.sh_ = Language("sh", "Q9301")  # Serbo-Croatian
langs.shi_ = Language("shi", "Q34152")  # Tachelhit
langs.shi_latn_ = Language("shi-latn", "Q34152")  # Tachelhit (Latin script)
langs.shi_tfng_ = Language("shi-tfng", "Q34152")  # Tachelhit (Tifinagh script)
langs.shn_ = Language("shn", "Q56482")  # Shan
langs.shy_ = Language("shy", "Q33274")  # Shawiya
langs.shy_latn_ = Language("shy-latn", "Q33274")  # Shawiya (Latin script)
langs.si_ = Language("si", "Q13267")  # Sinhala
langs.simple_ = Language("simple", "Q1860")  # Simple English
langs.skr_ = Language("skr", "Q33902")  # Saraiki
langs.skr_arab_ = Language("skr-arab", "Q33902")  # Saraiki (Arabic script)
langs.sli_ = Language("sli", "Q152965")  # Lower Silesian
langs.sm_ = Language("sm", "Q34011")  # Samoan
langs.sn_ = Language("sn", "Q34004")  # Shona
langs.so_ = Language("so", "Q13275")  # Somali
langs.sr_el_ = Language("sr-el", "Q9299")  # Serbian (Latin script)
langs.srn_ = Language("srn", "Q33989")  # Sranan Tongo
langs.srq_ = Language("srq", "Q3027953")  # Sirionó
langs.st_ = Language("st", "Q34340")  # Southern Sotho
langs.stq_ = Language("stq", "Q27154")  # Saterland Frisian
langs.sty_ = Language("sty", "Q4418344")  # Siberian Tatar
langs.su_ = Language("su", "Q34002")  # Sundanese
langs.sw_ = Language("sw", "Q7838")  # Swahili
langs.szl_ = Language("szl", "Q30319")  # Silesian
langs.szy_ = Language("szy", "Q718269")  # Sakizaya
langs.tay_ = Language("tay", "Q715766")  # Tayal
langs.tcy_ = Language("tcy", "Q34251")  # Tulu
langs.tet_ = Language("tet", "Q34125")  # Tetum
langs.tg_cyrl_ = Language("tg-cyrl", "Q9260")  # Tajik (Cyrillic script)
langs.tg_latn_ = Language("tg-latn", "Q9260")  # Tajik (Latin script)
langs.ti_ = Language("ti", "Q34124")  # Tigrinya
langs.tk_ = Language("tk", "Q9267")  # Turkmen
langs.tl_ = Language("tl", "Q34057")  # Tagalog
langs.tly_ = Language("tly", "Q34318")  # Talysh
langs.tly_cyrl_ = Language("tly-cyrl", "Q34318")  # толыши
langs.tn_ = Language("tn", "Q34137")  # Tswana
langs.to_ = Language("to", "Q34094")  # Tongan
langs.tpi_ = Language("tpi", "Q34159")  # Tok Pisin
langs.tru_ = Language("tru", "Q34040")  # Turoyo
langs.trv_ = Language("trv", "Q716686")  # Taroko
langs.ts_ = Language("ts", "Q34327")  # Tsonga
langs.tt_ = Language("tt", "Q25285")  # Tatar
langs.tt_cyrl_ = Language("tt-cyrl", "Q25285")  # Tatar (Cyrillic script)
langs.tt_latn_ = Language("tt-latn", "Q25285")  # Tatar (Latin script)
langs.tum_ = Language("tum", "Q34138")  # Tumbuka
langs.tvu_ = Language("tvu", "Q36632")  # Tunen
langs.ty_ = Language("ty", "Q34128")  # Tahitian
langs.tyv_ = Language("tyv", "Q34119")  # Tuvinian
langs.tzm_ = Language("tzm", "Q49741")  # Central Atlas Tamazight
langs.ug_ = Language("ug", "Q13263")  # Uyghur
langs.ug_arab_ = Language("ug-arab", "Q13263")  # Uyghur (Arabic script)
langs.ug_latn_ = Language("ug-latn", "Q13263")  # Uyghur (Latin script)
langs.uz_ = Language("uz", "Q9264")  # Uzbek
langs.uz_cyrl_ = Language("uz-cyrl", "Q9264")  # Uzbek (Cyrillic script)
langs.uz_latn_ = Language("uz-latn", "Q9264")  # Uzbek (Latin script)
langs.ve_ = Language("ve", "Q32704")  # Venda
langs.vec_ = Language("vec", "Q32724")  # Venetian
langs.vls_ = Language("vls", "Q100103")  # West Flemish
langs.vot_ = Language("vot", "Q32858")  # Votic
langs.vro_ = Language("vro", "Q32762")  # Võro
langs.vut_ = Language("vut", "Q36897")  # Vute
langs.war_ = Language("war", "Q34279")  # Waray
langs.wes_ = Language("wes", "Q35541")  # Pidgin (Cameroon)
langs.wls_ = Language("wls", "Q36979")  # Wallisian
langs.wo_ = Language("wo", "Q34257")  # Wolof
langs.wuu_ = Language("wuu", "Q34290")  # Wu Chinese
langs.wya_ = Language("wya", "Q1185119")  # Wyandot
langs.xal_ = Language("xal", "Q33634")  # Kalmyk
langs.xh_ = Language("xh", "Q13218")  # Xhosa
langs.xmf_ = Language("xmf", "Q13359")  # Mingrelian
langs.xsy_ = Language("xsy", "Q716695")  # Saisiyat
langs.yas_ = Language("yas", "Q36358")  # Nugunu
langs.yat_ = Language("yat", "Q8048020")  # Yambeta
langs.yav_ = Language("yav", "Q12953315")  # Yangben
langs.ybb_ = Language("ybb", "Q36917")  # Yemba
langs.yi_ = Language("yi", "Q8641")  # Yiddish
langs.yo_ = Language("yo", "Q34311")  # Yoruba
langs.yrl_ = Language("yrl", "Q34333")  # Nheengatu
langs.yue_ = Language("yue", "Q7033959")  # Cantonese
langs.za_ = Language("za", "Q13216")  # Zhuang
langs.zea_ = Language("zea", "Q237409")  # Zeelandic
langs.zgh_ = Language("zgh", "Q7598268")  # Standard Moroccan Tamazight
langs.zh_classical_ = Language("zh-classical", "Q37041")  # Classical Chinese
langs.zh_min_nan_ = Language("zh-min-nan", "Q36495")  # Chinese (Min Nan)
langs.zh_yue_ = Language("zh-yue", "Q7033959")  # Cantonese
langs.zu_ = Language("zu", "Q10179")  # Zulu
