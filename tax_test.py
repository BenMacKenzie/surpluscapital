import unittest


class MyTestCase(unittest.TestCase):
    def tes1(self):
        tax_rates = {'marginal': [(15,000, 0.2)], 'top': 0.2}
        m = tax.amount_of_deferred_asset_to_sell(1000, 0, tax_rates)
        self.assertEqual(m, 1000/.8)


if __name__ == '__main__':
    unittest.main()
