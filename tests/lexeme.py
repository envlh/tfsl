import unittest

from tfsl.claim import Claim
from tfsl.languages import langs
from tfsl.lexeme import Lexeme
from tfsl.lexemeform import LexemeForm
from tfsl.lexemesense import LexemeSense
from tfsl.statement import Statement

class TestLexemeMethods(unittest.TestCase):
    def setUp(self):
        self.rep1 = "दाम" @ langs.hi_
        self.rep2 = "دام" @ langs.ur_
        self.rep3 = "دم" @ langs.ur_
        self.feature1 = "Q110786"
        self.feature2 = "Q1751855"
        self.feature3 = "Q499327"
        self.category = "Q1084"
        self.property = "P1476"
        self.property2 = "P1683"
        self.value_mt1 = "দাম" @ langs.bn_
        self.value_mt2 = "dam" @ langs.en_
        self.rep4 = "দম" @ langs.bn_
        self.rep5 = "दम" @ langs.hi_
        self.rep6 = "damn" @ langs.en_
        self.rep7 = "dammerüng" @ langs.de_
        self.rep6 = "damme" @ langs.fr_
        self.rep7 = "dame" @ langs.es_
        self.rep8 = "damo" @ langs.it_
        self.rep9 = "dãme" @ langs.pt_

        self.lemmalist = [self.rep1, self.rep2]
        self.stmtlist = [Statement(self.property, self.value_mt1)]
        self.glosslist1 = [self.rep3, self.value_mt2]
        self.glosslist2 = [self.rep4, self.rep5]
        self.senselist = [LexemeSense(self.glosslist1), LexemeSense(self.glosslist2)]
        self.replist1 = [self.rep6, self.rep7]
        self.replist2 = [self.rep8, self.rep9]
        self.formlist = [LexemeForm(self.replist1), LexemeForm(self.replist2)]
        
        self.x = Lexeme(self.lemmalist, langs.bn_, self.category, self.stmtlist, self.senselist, self.formlist)

    def test_lexeme_create(self):
        self.assertCountEqual(self.x.lemmata.texts, self.lemmalist)
        self.assertEqual(self.x.language, langs.bn_)
        self.assertEqual(self.x.category, self.category)
        self.assertCountEqual(self.x.statements.statements, {self.property: self.stmtlist})
        self.assertEqual(self.x.senses, self.senselist)
        self.assertEqual(self.x.forms, self.formlist)

    def test_lexeme_add_statement(self):
        newstmt = Statement(self.property, self.value_mt2)
        y = self.x + newstmt
        self.assertCountEqual(y.lemmata.texts, self.lemmalist)
        self.assertEqual(y.language, langs.bn_)
        self.assertEqual(y.category, self.category)
        self.assertCountEqual(self.x.statements.statements, {self.property: self.stmtlist})
        self.assertCountEqual(y.statements.statements, {self.property: [self.stmtlist[0], newstmt]})
        self.assertEqual(y.senses, self.senselist)
        self.assertEqual(y.forms, self.formlist)
    
    def test_lexeme_add_sense(self):
        newsense = LexemeSense(self.glosslist2)
        y = self.x + newsense
        self.assertCountEqual(y.lemmata.texts, self.lemmalist)
        self.assertEqual(y.language, langs.bn_)
        self.assertEqual(y.category, self.category)
        self.assertCountEqual(y.statements.statements, {self.property: self.stmtlist})
        self.assertEqual(self.x.senses, self.senselist)
        self.assertEqual(y.senses, [self.senselist[0], self.senselist[1], newsense])
        self.assertEqual(y.forms, self.formlist)

    def test_lexeme_add_form(self):
        newform = LexemeForm(self.replist2)
        y = self.x + newform
        self.assertCountEqual(y.lemmata.texts, self.lemmalist)
        self.assertEqual(y.language, langs.bn_)
        self.assertEqual(y.category, self.category)
        self.assertCountEqual(y.statements.statements, {self.property: self.stmtlist})
        self.assertEqual(y.senses, self.senselist)
        self.assertEqual(self.x.forms, self.formlist)
        self.assertEqual(y.forms, [self.formlist[0], self.formlist[1], newform])
        
    # def test_lexeme_remove_statement(self):
    # def test_lexeme_remove_sense(self):
    # def test_lexeme_remove_form(self):
    # def test_lexeme_change_language(self):
    # def test_lexeme_change_category(self):

if __name__ == '__main__':
    unittest.main()
