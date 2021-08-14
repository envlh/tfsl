import unittest

from tfsl.languages import langs

class TestLanguageMethods(unittest.TestCase):
    def setUp(self):
        self.language = langs.bn_
        self.language2 = langs.ctg_
        self.language3 = langs.bn_

    def test_string_out(self):
        string_out = f'{self.language.code} ({self.language.item})'
        self.assertEqual(str(self.language), string_out)

    def test_compare_langs(self):
        self.assertEqual(self.language3, self.language)
        self.assertNotEqual(self.language2, self.language)

        self.assertEqual(self.language, "bn")
        self.assertNotEqual(self.language, "ctg")
        self.assertEqual(self.language2, "ctg")

        self.assertEqual(self.language, "Q9610")
        self.assertNotEqual(self.language, "Q33173")
        self.assertEqual(self.language2, "Q33173")

if __name__ == '__main__':
    unittest.main()
