""" Tests functionality from the tfsl.monolingualtext module. """

import unittest

from tfsl.languages import langs
import tfsl.monolingualtext
from tfsl.monolingualtext import MonolingualText as MT

class TestMonolingualTextMethods(unittest.TestCase):
    """ Holds tests of the MonolingualText class. """
    def setUp(self):
        self._text = "খেলা"
        self._language = langs.bn_

    def test_create_direct(self):
        """ Tests the MonolingualText constructor. """
        test_mt = MT(self._text, self._language)
        self.assertEqual(test_mt.text, self._text)
        self.assertEqual(test_mt.language, self._language)

    def test_create_indirect(self):
        """ Tests creating a MonolingualText with __matmul__. """
        test_mt = self._text @ self._language
        self.assertEqual(test_mt.text, self._text)
        self.assertEqual(test_mt.language, self._language)

    def test_change_language(self):
        """ Tests using __matmul__ to change the language of a MonolingualText. """
        test_mt = self._text @ self._language
        test_mt_ctg = test_mt @ langs.ctg_
        self.assertEqual(test_mt_ctg.text, test_mt.text)
        self.assertEqual(test_mt.language, langs.bn_)
        self.assertEqual(test_mt_ctg.language, langs.ctg_)

        test_mt @= langs.ctg_
        self.assertEqual(test_mt.text, self._text)
        self.assertEqual(test_mt.language, langs.ctg_)

    def test_jsonout(self):
        """ Tests serialization into JSON of a MonolingualText. """
        test_mt = self._text @ self._language
        test_mt_json = test_mt.__jsonout__()
        self.assertEqual(set(test_mt_json.keys()), {'text', 'language'})
        self.assertEqual(test_mt_json['text'], self._text)
        self.assertEqual(test_mt_json['language'], self._language.code)

class TestMonolingualTextHelpers(unittest.TestCase):
    """ Holds tests of functions that operate on monolingual text JSON. """
    def setUp(self):
        self.json_1 = {'text': 'hello', 'language': 'en'}
        self.json_2 = {'value': 'hello', 'language': 'en'}

    def test_is_mtvalue(self):
        """ Tests is_mtvalue. """
        self.assertTrue(tfsl.monolingualtext.is_mtvalue(self.json_1))
        self.assertFalse(tfsl.monolingualtext.is_mtvalue(self.json_2))

    def test_build_mtvalue(self):
        """ Tests build_mtvalue. """
        test_mt = tfsl.monolingualtext.build_mtvalue(self.json_1)
        self.assertEqual(test_mt.text, self.json_1['text'])
        self.assertEqual(test_mt.language.code, self.json_1['language'])

    def test_build_lemma(self):
        """ Tests build_lemma. """
        test_mt = tfsl.monolingualtext.build_lemma(self.json_2)
        self.assertEqual(test_mt.text, self.json_2['value'])
        self.assertEqual(test_mt.language.code, self.json_2['language'])

if __name__ == '__main__':
    unittest.main()
