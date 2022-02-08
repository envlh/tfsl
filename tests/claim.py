import json
import unittest

from tfsl.languages import langs
from tfsl.claim import Claim

class TestClaimMethods(unittest.TestCase):
    def setUp(self):
        self.property = "P1476"
        self.value_mt = "চাকা" @ langs.bn_

    def test_claim_mt_direct(self):
        x = Claim(self.property, self.value_mt)
        self.assertEqual(x.property, self.property)
        self.assertEqual(x.value, self.value_mt)
        
    def test_claim_novalue(self):
        x = Claim(self.property, False)
        self.assertEqual(x.property, self.property)
        self.assertFalse(x.value)
    
    def test_claim_somevalue(self):
        x = Claim(self.property, True)
        self.assertEqual(x.property, self.property)
        self.assertIsInstance(x.value, bool)
        self.assertTrue(x.value)

if __name__ == '__main__':
    unittest.main()
