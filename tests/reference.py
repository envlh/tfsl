import unittest

from tfsl.claim import Claim
from tfsl.languages import langs
from tfsl.reference import Reference

class TestReferenceMethods(unittest.TestCase):
    def setUp(self):
        self._language = langs.bn_
        self._text = "পাখি" @ langs.bn_
        self._text2 = "পাকা" @ langs.bn_
        self._text3 = "পেঁপে" @ langs.bn_
        self._text4 = "খায়" @ langs.bn_
        self.prop1 = "P1476"
        self.prop2 = "P1448"
        self.prop3 = "P1638"
        self.claim1 = Claim(self.prop1,self._text)
        self.claim2 = Claim(self.prop1,self._text2)
        self.claim3 = Claim(self.prop2,self._text3)
        self.claim4 = Claim(self.prop3,self._text4)

    def test_one_statement_ref(self):
        x = Reference(self.claim1)
        self.assertCountEqual(x[self.prop1], [self.claim1])
    
    def test_multiple_statement_ref(self):
        x = Reference(self.claim1, self.claim2, self.claim3, self.claim4)
        self.assertCountEqual(x[self.prop1], [self.claim1, self.claim2])
        self.assertCountEqual(x[self.prop2], [self.claim3])
        self.assertCountEqual(x[self.prop3], [self.claim4])

    def test_ref_add_statement(self):
        newclaim = Claim(self.prop3, self._text3)

        x = Reference(self.claim1, self.claim2, self.claim3, self.claim4)
        y = x + newclaim
        
        self.assertCountEqual(y[self.prop1], [self.claim1, self.claim2])
        self.assertCountEqual(y[self.prop2], [self.claim3])
        self.assertCountEqual(x[self.prop3], [self.claim4])
        self.assertCountEqual(y[self.prop3], [self.claim4, newclaim])

    def test_ref_remove_statement(self):
        x = Reference(self.claim1, self.claim2, self.claim3, self.claim4)
        y = x - self.claim4
        
        self.assertCountEqual(y[self.prop1], [self.claim1, self.claim2])
        self.assertCountEqual(y[self.prop2], [self.claim3])
        self.assertCountEqual(x[self.prop3], [self.claim4])
        self.assertNotIn(self.prop3, y)

    def test_remove_stmt(self):
        x = Reference(self.claim1, self.claim2)
        del x[self.prop1]
        self.assertNotIn(self.prop1, x)
        self.assertNotIn(self.claim1, x)

        x = Reference(self.claim1, self.claim2)
        del x[Claim(self.prop1, self._text)]
        self.assertNotIn(self.claim1, x)
        self.assertIn(self.claim2, x)

if __name__ == '__main__':
    unittest.main()
