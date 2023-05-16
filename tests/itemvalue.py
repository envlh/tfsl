""" Tests functionality from the tfsl.itemvalue module. """

import unittest

import tfsl.interfaces as I
import tfsl.itemvalue
from tfsl.itemvalue import ItemValue as IV

class TestItemValueMethods(unittest.TestCase):
    """ Holds tests of the ItemValue class. """
    def setUp(self):
        self._qid = I.Qid('Q123')
        self._pid = I.Pid('P123')
        self._lid = I.Lid('L123')
        self._lfid = I.LFid('L123-F4')
        self._lsid = I.LSid('L123-S4')

    def test_create(self):
        """ Tests the ItemValue constructor. """
        for identifier, idtype in zip(
            [self._qid, self._pid, self._lid, self._lfid, self._lsid],
            ['item', 'property', 'lexeme', 'form', 'sense']
        ):
            with self.subTest(identifier=identifier, idtype=idtype):
                test_iv = IV(identifier)
                self.assertEqual(test_iv.id, identifier)
                self.assertEqual(test_iv.type, idtype)

    def test_jsonout(self):
        """ Tests serialization into JSON of an ItemValue. """
        for identifier, idtype in zip(
            [self._qid, self._pid, self._lid],
            ['item', 'property', 'lexeme']
        ):
            with self.subTest(identifier=identifier, idtype=idtype):
                test_iv_json = IV(identifier).__jsonout__()
                self.assertEqual(test_iv_json['entity-type'], idtype)
                self.assertEqual(test_iv_json['id'], identifier)
                self.assertEqual(test_iv_json['numeric-id'], 123)

        for identifier, idtype in zip(
            [self._lfid, self._lsid],
            ['form', 'sense']
        ):
            with self.subTest(identifier=identifier, idtype=idtype):
                test_iv_json = IV(identifier).__jsonout__()
                self.assertEqual(test_iv_json['entity-type'], idtype)
                self.assertEqual(test_iv_json['id'], identifier)
                self.assertFalse('numeric-id' in test_iv_json)

class TestItemValueHelpers(unittest.TestCase):
    """ Holds tests of functions that operate on item value JSON. """
    def setUp(self):
        self.json_1 = {'entity-type': 'item', 'id': 'Q456'}
        self.json_2 = {'entity-type': 'form', 'id': 'L456-F7'}
        self.json_3 = {'entity-kind': 'form', 'id': 'L456-F7'}

    def test_is_itemvalue(self):
        """ Tests is_itemvalue. """
        self.assertTrue(tfsl.itemvalue.is_itemvalue(self.json_1))
        self.assertTrue(tfsl.itemvalue.is_itemvalue(self.json_2))
        self.assertFalse(tfsl.itemvalue.is_itemvalue(self.json_3))

    def test_build_itemvalue(self):
        """ Tests build_itemvalue. """
        test_mt1 = tfsl.itemvalue.build_itemvalue(self.json_1)
        self.assertEqual(test_mt1.type, self.json_1['entity-type'])
        self.assertEqual(test_mt1.id, self.json_1['id'])
        test_mt2 = tfsl.itemvalue.build_itemvalue(self.json_2)
        self.assertEqual(test_mt2.type, self.json_2['entity-type'])
        self.assertEqual(test_mt2.id, self.json_2['id'])

if __name__ == '__main__':
    unittest.main()
