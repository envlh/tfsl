import unittest

from tfsl.claim import Claim
from tfsl.languages import langs
from tfsl.lexemesense import LexemeSense
from tfsl.statement import Statement

class TestSenseMethods(unittest.TestCase):
    def setUp(self):
        self.rep1 = "दाम" @ langs.hi_
        self.rep2 = "دام" @ langs.ur_
        self.rep3 = "دم" @ langs.ur_
        self.feature1 = "Q110786"
        self.feature2 = "Q1751855"
        self.feature3 = "Q499327"
        self.property = "P1476"
        self.value_mt1 = "দাম" @ langs.bn_
        self.value_mt2 = "dam" @ langs.en_

    def test_lexemesense_create(self):
        glosslist = [self.rep1, self.rep2]
        stmtlist = [Statement(self.property, self.value_mt1)]

        x = LexemeSense(glosslist, stmtlist)

        self.assertEqual(x.glosses, glosslist)
        self.assertIn(self.rep1, x)
        self.assertIn(langs.hi_, x)
        self.assertEqual(x.statements, {self.property: [stmtlist[0]]})
        self.assertIn(stmtlist[0], x)

    def test_lexemesense_add_gloss(self):
        glosslist = [self.rep1, self.rep2]
        stmtlist = [Statement(self.property, self.value_mt1)]

        x = LexemeSense(glosslist, stmtlist)
        y = x + self.value_mt1

        self.assertCountEqual(x.glosses.texts, glosslist)
        self.assertCountEqual(y.glosses.texts, [glosslist[0], glosslist[1], self.value_mt1])
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

    def test_lexemesense_add_statement(self):
        glosslist = [self.rep1, self.rep2]
        stmtlist = [Statement(self.property, self.value_mt1)]
        newstmt = Statement(self.property, self.value_mt2)

        x = LexemeSense(glosslist, stmtlist)
        y = x + newstmt

        self.assertCountEqual(y.glosses.texts, glosslist)
        self.assertEqual(x.statements, {self.property: stmtlist})
        self.assertEqual(y.statements, {self.property: [stmtlist[0], newstmt]})

    def test_lexemesense_remove_gloss(self):
        glosslist = [self.rep1, self.rep2]
        stmtlist = [Statement(self.property, self.value_mt1)]

        x = LexemeSense(glosslist, stmtlist)
        y = x - self.rep2

        self.assertCountEqual(x.glosses.texts, glosslist)
        self.assertCountEqual(y.glosses.texts, [glosslist[0]])
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

        x = LexemeSense(glosslist, stmtlist)
        y = x - langs.ur_

        self.assertCountEqual(x.glosses.texts, glosslist)
        self.assertCountEqual(y.glosses.texts, [glosslist[0]])
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

    def test_lexemesense_remove_statement(self):
        glosslist = [self.rep1, self.rep2]
        stmtlist = [Statement(self.property, self.value_mt1)]
        newstmt = Statement(self.property, self.value_mt2)

        x = LexemeSense(glosslist, [stmtlist[0], newstmt])
        y = x - newstmt

        self.assertCountEqual(y.glosses.texts, glosslist)
        self.assertEqual(x.statements, {self.property: [stmtlist[0], newstmt]})
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

        x = LexemeSense(glosslist, [stmtlist[0], newstmt])
        y = x - self.property

        self.assertCountEqual(y.glosses.texts, glosslist)
        self.assertEqual(x.statements, {self.property: [stmtlist[0], newstmt]})
        self.assertEqual(y.statements, {})

    def test_lexemesense_overwrite_gloss(self):
        glosslist = [self.rep1, self.rep2]
        stmtlist = [Statement(self.property, self.value_mt1)]

        x = LexemeSense(glosslist, stmtlist)
        y = x + self.rep3

        self.assertCountEqual(x.glosses.texts, glosslist)
        self.assertCountEqual(y.glosses.texts, [glosslist[0], self.rep3])
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

if __name__ == '__main__':
    unittest.main()
