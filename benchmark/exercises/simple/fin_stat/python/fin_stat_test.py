import unittest
from finance_and_accounting import calculate_liabilities_and_equity

class TestFinanceAndAccounting(unittest.TestCase):
    def test_calculate_liabilities_and_equity(self):
        assets = [100, 200, 300, 400, 500]
        debt_equity_ratio = 0.5
        result = calculate_liabilities_and_equity(assets, debt_equity_ratio)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]['total_assets'], 100)
        self.assertEqual(result[0]['liabilities'], 33)
        self.assertEqual(result[0]['equity'], 67)
        self.assertEqual(result[4]['total_assets'], 500)
        self.assertEqual(result[4]['liabilities'], 167)
        self.assertEqual(result[4]['equity'], 333)

    def test_calculate_liabilities_and_equity_with_zero_debt_equity_ratio(self):
        assets = [100, 200, 300, 400, 500]
        debt_equity_ratio = 0
        result = calculate_liabilities_and_equity(assets, debt_equity_ratio)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]['total_assets'], 100)
        self.assertEqual(result[0]['liabilities'], 0)
        self.assertEqual(result[0]['equity'], 100)
        self.assertEqual(result[4]['total_assets'], 500)
        self.assertEqual(result[4]['liabilities'], 0)
        self.assertEqual(result[4]['equity'], 500)

    def test_calculate_liabilities_and_equity_with_large_assets(self):
        assets = [1000000, 2000000, 3000000, 4000000, 5000000]
        debt_equity_ratio = 0.5
        result = calculate_liabilities_and_equity(assets, debt_equity_ratio)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]['total_assets'], 1000000)
        self.assertEqual(result[0]['liabilities'], 333333)
        self.assertEqual(result[0]['equity'], 666667)
        self.assertEqual(result[4]['total_assets'], 5000000)
        self.assertEqual(result[4]['liabilities'], 1666667)
        self.assertEqual(result[4]['equity'], 3333333)

    def test_calculate_liabilities_and_equity_with_100_periods(self):
        assets = [100] * 100
        debt_equity_ratio = 0.5
        result = calculate_liabilities_and_equity(assets, debt_equity_ratio)
        self.assertEqual(len(result), 100)
        for period in result:
            self.assertEqual(period['total_assets'], 100)
            self.assertEqual(period['liabilities'], 33)
            self.assertEqual(period['equity'], 67)

if __name__ == '__main__':
    unittest.main()