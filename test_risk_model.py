"""

Test Cases:

1) A transaction with gift card, no loyalty tier
and late-night purchase time should produce a high likelihood score.

2) A transaction with Debit Card, VIP loyalty tier, and daytime purchase
time should produce a low likelihood score.

"""

import unittest
from transaction_risk_analysis import (
    calculate_likelihood,
    calculate_impact,
    calculate_risk,
    categorize_risk,
    detect_sql_injection
)

class TestRiskModel(unittest.TestCase):

    def test_calculate_impact(self):
        self.assertEqual(calculate_impact(25), 1)
        self.assertEqual(calculate_impact(100), 2)
        self.assertEqual(calculate_impact(250), 3)
        self.assertEqual(calculate_impact(400), 4)
        self.assertEqual(calculate_impact(600), 5)

    def test_calculate_risk(self):
        self.assertEqual(calculate_risk(2, 3), 6)
        self.assertEqual(calculate_risk(5, 5), 25)

    def test_categorize_risk(self):
        self.assertEqual(categorize_risk(2), "Low")
        self.assertEqual(categorize_risk(5), "Moderate")
        self.assertEqual(categorize_risk(10), "High")
        self.assertEqual(categorize_risk(20), "Severe")

    def test_calculate_likelihood(self):
        self.assertEqual(calculate_likelihood("Gift Card", "None", "23:30:00"), 5)
        self.assertEqual(calculate_likelihood("Mobile Payment", "Bronze", "14:00:00"), 2)
        self.assertEqual(calculate_likelihood("Credit Card", "VIP", "13:00:00"), 0)

class TestThreatSimulation(unittest.TestCase):

        def test_basic_sql_injection_detected(self):
            payload = "' OR '1'='1"
            self.assertTrue(detect_sql_injection(payload))

        def test_or_one_equals_one_detected(self):
            payload = "' OR 1=1 --"
            self.assertTrue(detect_sql_injection(payload))

        def test_union_attack_detected(self):
            payload = "' UNION SELECT * FROM transactions --"
            self.assertTrue(detect_sql_injection(payload))

        def test_drop_table_detected(self):
            payload = "'; DROP TABLE transactions; --"
            self.assertTrue(detect_sql_injection(payload))

        def test_normal_customer_id_not_detected(self):
            payload = "CUST12345"
            self.assertFalse(detect_sql_injection(payload))

if __name__ == "__main__":
    unittest.main()