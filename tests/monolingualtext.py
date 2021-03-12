import json
import unittest

from tfsl.languages import langs
from tfsl.monolingualtext import MonolingualText as MT

class TestMonolingualTextMethods(unittest.TestCase):
    def setUp(self):
        self._text = "খেলা"
        self._language = langs.bn_
    
    def test_create_direct(self):
        x = MT(self._text, self._language)
        self.assertEqual(x.text, self._text)
        self.assertEqual(x.language, self._language)

    def test_create_indirect(self):
        x = self._text @ self._language
        self.assertEqual(x.text, self._text)
        self.assertEqual(x.language, self._language)

    def test_change_language(self):
        x = self._text @ self._language
        y = x @ langs.ctg_
        self.assertEqual(y.text, x.text)
        self.assertEqual(x.language, langs.bn_)
        self.assertEqual(y.language, langs.ctg_)

        x @= langs.ctg_
        self.assertEqual(x.text, self._text)
        self.assertEqual(x.language, langs.ctg_)

if __name__ == '__main__':
    unittest.main()
