import unittest
import tax

class MyTestCase(unittest.TestCase):
    def test1(self):
        tax_rates = {'marginal': [(10000, 0.2)], 'top': 0.2}
        m = tax.amount_of_deferred_asset_to_sell(1000, 0, tax_rates)
        self.assertEqual(m, 1250)


    def test2(self):
        tax_rates = {'marginal': [(10000, 0.2)], 'top': 0.4}
        m = tax.amount_of_deferred_asset_to_sell(15000, 0, tax_rates)
        self.assertEqual(m, 10000 + 7000 / 0.6)

    def test3(self):
        tax_rates = {'marginal': [(10000, 0.2)], 'top': 0.4}
        m = tax.amount_of_deferred_asset_to_sell(10000, 20000, tax_rates)
        self.assertEqual(m, 10000/0.6)


    def test4(self):
        tax_rates = {'marginal': [(10000, 0.1), (20000, 0.2)], 'top': 0.4}
        m = tax.amount_of_deferred_asset_to_sell(15000, 10000, tax_rates)
        self.assertEqual(m, 10000 + 7000 / 0.6)

    def test5(self):
        tax_rates = {'marginal': [(10000, 0.2), (30000, 0.4)], 'top': 0.5}
        m = tax.amount_of_deferred_asset_to_sell(15000, 0, tax_rates)
        self.assertEqual(m, 10000 + 7000 / 0.6)


    def test6(self):
        tax_rates = tax.get_tax_rates('Ontario')
        print(tax_rates)


if __name__ == '__main__':
    unittest.main()
