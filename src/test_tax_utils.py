import unittest

from tax_utils import get_tax_rates


class MyTestCase(unittest.TestCase):
    def test_something(self):
        rates = get_tax_rates('Ontario')
        print(rates)


if __name__ == '__main__':
    unittest.main()
