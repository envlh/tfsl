import json
import unittest

from tfsl.quantityvalue import QuantityValue as QV

class TestQuantityValueMethods(unittest.TestCase):
    def setUp(self):
        self._positivemagnitude = 10
        self._negativemagnitude = -10
        self._tolerance = 0.5
        self._unit = 'Q174728'