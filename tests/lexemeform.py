import unittest

from tfsl.claim import Claim
from tfsl.languages import langs
from tfsl.lexemeform import LexemeForm
from tfsl.statement import Statement

class TestFormMethods(unittest.TestCase):
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
    
    def test_lexemeform_create(self):
        replist = [self.rep1, self.rep2]
        featlist = [self.feature1, self.feature2]
        stmtlist = [Statement(self.property, self.value_mt1)]

        x = LexemeForm(replist, featlist, stmtlist)
        
        self.assertCountEqual(x.representations.texts, replist)
        self.assertIn(self.rep1, x)
        self.assertIn(langs.hi_, x)
        self.assertCountEqual(x.features, featlist)
        self.assertIn(self.feature1, x)
        self.assertEqual(x.statements, {self.property: [stmtlist[0]]})
        self.assertIn(self.property, x)
    
    def test_lexemeform_add_rep(self):
        replist = [self.rep1, self.rep2]
        featlist = [self.feature1, self.feature2]
        stmtlist = [Statement(self.property, self.value_mt1)]
        
        x = LexemeForm(replist, featlist, stmtlist)
        y = x + self.value_mt1
        self.assertCountEqual(x.representations.texts, replist)
        self.assertCountEqual(y.representations.texts, [replist[0], replist[1], self.value_mt1])
        self.assertCountEqual(y.features, featlist)
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

    def test_lexemeform_add_feature(self):
        replist = [self.rep1, self.rep2]
        featlist = [self.feature1, self.feature2]
        stmtlist = [Statement(self.property, self.value_mt1)]
        
        x = LexemeForm(replist, featlist, stmtlist)
        y = x + self.feature3

        self.assertCountEqual(y.representations.texts, replist)
        self.assertCountEqual(x.features, featlist)
        self.assertCountEqual(y.features, [featlist[0], featlist[1], self.feature3])
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

    def test_lexemeform_add_statement(self):
        replist = [self.rep1, self.rep2]
        featlist = [self.feature1, self.feature2]
        stmtlist = [Statement(self.property, self.value_mt1)]
        newstmt = Statement(self.property, self.value_mt2)
        
        x = LexemeForm(replist, featlist, stmtlist)
        y = x + newstmt

        self.assertCountEqual(y.representations.texts, replist)
        self.assertCountEqual(y.features, featlist)
        self.assertEqual(x.statements, {self.property: stmtlist})
        self.assertEqual(y.statements, {self.property: [stmtlist[0], newstmt]})

    def test_lexemeform_remove_rep(self):
        replist = [self.rep1, self.rep2]
        featlist = [self.feature1, self.feature2]
        stmtlist = [Statement(self.property, self.value_mt1), Statement(self.property, self.value_mt2)]
        
        x = LexemeForm(replist, featlist, stmtlist)
        y = x - self.rep2

        self.assertCountEqual(x.representations.texts, replist)
        self.assertCountEqual(y.representations.texts, [replist[0]])
        self.assertCountEqual(y.features, featlist)
        self.assertEqual(y.statements, {self.property: [stmtlist[0], stmtlist[1]]})
        
        x = LexemeForm(replist, featlist, stmtlist)
        y = x - langs.ur_

        self.assertCountEqual(y.representations.texts, [replist[0]])
        self.assertCountEqual(y.features, featlist)
        self.assertEqual(y.statements, {self.property: [stmtlist[0], stmtlist[1]]})

    def test_lexemeform_remove_feature(self):
        replist = [self.rep1, self.rep2]
        featlist = [self.feature1, self.feature2]
        stmtlist = [Statement(self.property, self.value_mt1)]
        
        x = LexemeForm(replist, featlist, stmtlist)
        y = x - self.feature2

        self.assertCountEqual(y.representations.texts, replist)
        self.assertCountEqual(x.features, featlist)
        self.assertCountEqual(y.features, [featlist[0]])
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

    def test_lexemeform_remove_statement(self):
        replist = [self.rep1, self.rep2]
        featlist = [self.feature1, self.feature2]
        stmtlist = [Statement(self.property, self.value_mt1)]
        newstmt = Statement(self.property, self.value_mt2)
        
        x = LexemeForm(replist, featlist, [stmtlist[0], newstmt])
        y = x - newstmt

        self.assertCountEqual(y.representations.texts, replist)
        self.assertCountEqual(y.features, featlist)
        self.assertEqual(x.statements, {self.property: [stmtlist[0], newstmt]})
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

        x = LexemeForm(replist, featlist, [stmtlist[0], newstmt])
        y = x - self.property

        self.assertCountEqual(y.representations.texts, replist)
        self.assertCountEqual(y.features, featlist)
        self.assertEqual(y.statements, {})

    def test_lexemeform_overwrite_rep(self):
        # TODO: add warning?
        replist = [self.rep1, self.rep2]
        featlist = [self.feature1, self.feature2]
        stmtlist = [Statement(self.property, self.value_mt1)]
        newstmt = Statement(self.property, self.value_mt2)
        
        x = LexemeForm(replist, featlist, stmtlist)
        y = x + self.rep3

        self.assertCountEqual(x.representations.texts, replist)
        self.assertCountEqual(y.representations.texts, [replist[0], self.rep3])
        self.assertCountEqual(y.features, featlist)
        self.assertEqual(y.statements, {self.property: [stmtlist[0]]})

if __name__ == '__main__':
    unittest.main()

