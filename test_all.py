import unittest

from tests import *

if __name__ == '__main__':
    suite = unittest.TestLoader().discover("tests", pattern = "*")
    runner = unittest.TextTestRunner()
    runner.run(suite)