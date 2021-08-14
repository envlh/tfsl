import unittest

from tfsl.languages import langs
from tfsl.monolingualtext import MonolingualText as MT

class TestMonolingualTextMethods(unittest.TestCase):
    def setUp(self):
        self._text = "খেলা"
        self._language = langs.bn_

    def test_create_direct(self):
        test_mt = MT(self._text, self._language)
        self.assertEqual(test_mt.text, self._text)
        self.assertEqual(test_mt.language, self._language)

    def test_create_indirect(self):
        test_mt = self._text @ self._language
        self.assertEqual(test_mt.text, self._text)
        self.assertEqual(test_mt.language, self._language)

    def test_change_language(self):
        test_mt = self._text @ self._language
        test_mt_ctg = test_mt @ langs.ctg_
        self.assertEqual(test_mt_ctg.text, test_mt.text)
        self.assertEqual(test_mt.language, langs.bn_)
        self.assertEqual(test_mt_ctg.language, langs.ctg_)

        test_mt @= langs.ctg_
        self.assertEqual(test_mt.text, self._text)
        self.assertEqual(test_mt.language, langs.ctg_)

if __name__ == '__main__':
    unittest.main()
