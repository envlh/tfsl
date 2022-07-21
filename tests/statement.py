import unittest

from tfsl.claim import Claim
from tfsl.languages import langs
from tfsl.reference import Reference
from tfsl.statement import Statement, Rank

class TestStatementMethods(unittest.TestCase):
    def setUp(self):
        self.property = "P1476"
        self.value_mt = "টাকা" @ langs.bn_
        self.value_mt2 = "রূপী" @ langs.bn_
        self.value_q1 = "পয়সা" @ langs.bn_
        self.value_q2 = "মুদ্রা" @ langs.bn_
        self.value_r1 = "ব্যাংক" @ langs.bn_

    def test_statement_basic(self):
        x = Statement(self.property, self.value_mt)
        self.assertEqual(x.property, self.property)
        self.assertEqual(x.value, self.value_mt)
        self.assertEqual(x.rank, Rank.Normal)
        self.assertEqual(x.qualifiers, {})
        self.assertCountEqual(x.references, [])

    def test_statement_complex(self):
        quallist = [Claim("P1448", self.value_q1), Claim("P1683", self.value_q2)]
        reflist = [Reference(Claim("P1922", self.value_r1))]
        x = Statement(self.property, self.value_mt, Rank.Preferred, quallist, reflist)
        self.assertEqual(x.property, self.property)
        self.assertEqual(x.value, self.value_mt)
        self.assertEqual(x.rank, Rank.Preferred)
        self.assertEqual(x.qualifiers, {"P1448": [quallist[0]], "P1683": [quallist[1]]})
        self.assertCountEqual(x.references, reflist)

        x = Statement(self.property, self.value_mt, references=reflist, rank=Rank.Preferred)
        self.assertEqual(x.property, self.property)
        self.assertEqual(x.value, self.value_mt)
        self.assertEqual(x.rank, Rank.Preferred)
        self.assertEqual(x.qualifiers, {})
        self.assertCountEqual(x.references, reflist)

    def test_statement_add_qualifier(self):
        quallist = [Claim("P1448", self.value_q1)]
        newclaim = Claim("P1683", self.value_q2)
        reflist = [Reference(Claim("P1922", self.value_r1))]

        x = Statement(self.property, self.value_mt, Rank.Deprecated, quallist, reflist)
        x += newclaim

        self.assertEqual(x.property, self.property)
        self.assertEqual(x.value, self.value_mt)
        self.assertEqual(x.rank, Rank.Deprecated)
        self.assertEqual(x.qualifiers, {"P1448": [quallist[0]], "P1683": [newclaim]})
        self.assertCountEqual(x.references, reflist)

        x = Statement(self.property, self.value_mt, Rank.Deprecated, quallist, reflist)
        y = x + newclaim
        self.assertEqual(y.property, self.property)
        self.assertEqual(y.value, self.value_mt)
        self.assertEqual(y.rank, Rank.Deprecated)
        self.assertEqual(y.qualifiers, {"P1448": [quallist[0]], "P1683": [newclaim]})
        self.assertCountEqual(y.references, reflist)
    
    def test_statement_remove_qualifier(self):
        newclaim = Claim("P1683", self.value_q2)
        quallist = [Claim("P1448", self.value_q1), newclaim]
        reflist = [Reference(Claim("P1922", self.value_r1))]

        x = Statement(self.property, self.value_mt, Rank.Deprecated, quallist, reflist)
        x -= newclaim

        self.assertEqual(x.property, self.property)
        self.assertEqual(x.value, self.value_mt)
        self.assertEqual(x.rank, Rank.Deprecated)
        self.assertEqual(x.qualifiers, {"P1448": [quallist[0]]})
        self.assertCountEqual(x.references, reflist)

        x = Statement(self.property, self.value_mt, Rank.Deprecated, quallist, reflist)
        y = x - newclaim
        self.assertEqual(y.property, self.property)
        self.assertEqual(y.value, self.value_mt)
        self.assertEqual(y.rank, Rank.Deprecated)
        self.assertEqual(y.qualifiers, {"P1448": [quallist[0]]})
        self.assertCountEqual(y.references, reflist)

    def test_statement_add_reference(self):
        quallist = [Claim("P1448", self.value_q1)]
        reflist = [Reference(Claim("P1922", self.value_r1))]
        newref = Reference(Claim("P1683", self.value_q2))

        x = Statement(self.property, self.value_mt, Rank.Deprecated, quallist, reflist)
        x += newref

        self.assertEqual(x.property, self.property)
        self.assertEqual(x.value, self.value_mt)
        self.assertEqual(x.rank, Rank.Deprecated)
        self.assertEqual(x.qualifiers, {"P1448": [quallist[0]]})
        self.assertCountEqual(x.references, [reflist[0], newref])

        x = Statement(self.property, self.value_mt, Rank.Deprecated, quallist, reflist)
        y = x + newref
        self.assertEqual(y.property, self.property)
        self.assertEqual(y.value, self.value_mt)
        self.assertEqual(y.rank, Rank.Deprecated)
        self.assertEqual(y.qualifiers, {"P1448": [quallist[0]]})
        self.assertCountEqual(y.references, [reflist[0], newref])

    def test_statement_remove_reference(self):
        quallist = [Claim("P1448", self.value_q1)]
        newref = Reference(Claim("P1683", self.value_q2))
        reflist = [Reference(Claim("P1922", self.value_r1)), newref]

        x = Statement(self.property, self.value_mt, Rank.Deprecated, quallist, reflist)
        x -= newref

        self.assertEqual(x.property, self.property)
        self.assertEqual(x.value, self.value_mt)
        self.assertEqual(x.rank, Rank.Deprecated)
        self.assertEqual(x.qualifiers, {"P1448": [quallist[0]]})
        self.assertCountEqual(x.references, [reflist[0]])

        x = Statement(self.property, self.value_mt, Rank.Deprecated, quallist, reflist)
        y = x - newref
        self.assertEqual(y.property, self.property)
        self.assertEqual(y.value, self.value_mt)
        self.assertEqual(y.rank, Rank.Deprecated)
        self.assertEqual(y.qualifiers, {"P1448": [quallist[0]]})
        self.assertCountEqual(y.references, [reflist[0]])
    
    def test_statement_change_rank(self):
        x = Statement(self.property, self.value_mt)
        x @= Rank.Preferred
        
        self.assertEqual(x.property, self.property)
        self.assertEqual(x.value, self.value_mt)
        self.assertEqual(x.rank, Rank.Preferred)
        self.assertEqual(x.qualifiers, {})
        self.assertCountEqual(x.references, [])

        y = x @ Rank.Deprecated
        self.assertEqual(y.property, self.property)
        self.assertEqual(y.value, self.value_mt)
        self.assertEqual(y.rank, Rank.Deprecated)
        self.assertEqual(y.qualifiers, {})
        self.assertCountEqual(y.references, [])
    
    # TODO: once loading items from Wikidata, verify that setting value to different type disallowed

if __name__ == '__main__':
    unittest.main()
