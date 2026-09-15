"""
Unit tests for etl.parsers.currency, run against the string shapes named
explicitly in CLAUDE.md rule 6. Once the raw CPPP dump is downloaded and
verified, extend this file with ~50 real strings sampled from the actual
contract_value/emd columns (H6-H18 D block) rather than only the
documented shapes below.
"""
import unittest
from decimal import Decimal

from etl.parsers.currency import RejectLog, parse_currency


class TestParseCurrency(unittest.TestCase):
    def test_indian_grouped_string(self):
        self.assertEqual(parse_currency("1,23,45,678.00"), Decimal("12345678.00"))

    def test_western_grouped_string(self):
        self.assertEqual(parse_currency("1,234,567.89"), Decimal("1234567.89"))

    def test_rs_prefix_with_grouping(self):
        self.assertEqual(parse_currency("Rs. 45,00,000"), Decimal("4500000"))

    def test_rs_no_dot(self):
        self.assertEqual(parse_currency("Rs 45,00,000"), Decimal("4500000"))

    def test_inr_prefix(self):
        self.assertEqual(parse_currency("INR 45,00,000"), Decimal("4500000"))

    def test_rupee_symbol(self):
        self.assertEqual(parse_currency("₹45,00,000"), Decimal("4500000"))

    def test_plain_integer(self):
        self.assertEqual(parse_currency("500000"), Decimal("500000"))

    def test_plain_decimal(self):
        self.assertEqual(parse_currency("500000.50"), Decimal("500000.50"))

    def test_lakh_word(self):
        self.assertEqual(parse_currency("45 Lakh"), Decimal("4500000"))

    def test_lakh_decimal(self):
        self.assertEqual(parse_currency("4.5 Lakh"), Decimal("450000"))

    def test_lakhs_plural(self):
        self.assertEqual(parse_currency("45 Lakhs"), Decimal("4500000"))

    def test_lac_spelling(self):
        self.assertEqual(parse_currency("45 Lac"), Decimal("4500000"))

    def test_crore_word(self):
        self.assertEqual(parse_currency("2 Crore"), Decimal("20000000"))

    def test_crore_decimal(self):
        self.assertEqual(parse_currency("2.3 Cr"), Decimal("23000000"))

    def test_na_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_currency("NA", log))
        self.assertEqual(log.rejections[0].reason, "explicit_na")

    def test_n_slash_a_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_currency("N/A", log))
        self.assertEqual(log.rejections[0].reason, "explicit_na")

    def test_empty_string_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_currency("", log))
        self.assertEqual(log.rejections[0].reason, "empty")

    def test_dash_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_currency("-", log))
        self.assertEqual(log.rejections[0].reason, "explicit_na")

    def test_none_input_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_currency(None, log))
        self.assertEqual(log.rejections[0].reason, "null_input")

    def test_garbage_string_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_currency("as per tender document", log))
        self.assertEqual(log.rejections[0].reason, "unparseable")

    def test_negative_value_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_currency("-5000", log))
        self.assertEqual(log.rejections[0].reason, "negative_value")

    def test_zero_is_valid(self):
        # F11 treats zero EMD as a real, meaningful value (low deterrence),
        # not a parse failure.
        self.assertEqual(parse_currency("0"), Decimal("0"))

    def test_trailing_only_notation(self):
        self.assertEqual(parse_currency("Rs.50,000/-"), Decimal("50000"))

    def test_trailing_only_notation_no_dash(self):
        self.assertEqual(parse_currency("Rs. 50,000/"), Decimal("50000"))

    def test_whitespace_padding(self):
        self.assertEqual(parse_currency("  45,00,000  "), Decimal("4500000"))

    def test_numeric_passthrough(self):
        self.assertEqual(parse_currency(500000), Decimal("500000"))

    def test_reject_log_accumulates_multiple(self):
        log = RejectLog()
        parse_currency("NA", log)
        parse_currency("", log)
        parse_currency("garbage!!", log)
        self.assertEqual(len(log.rejections), 3)
        rows = log.to_rows()
        self.assertEqual(rows[0]["raw"], "NA")


if __name__ == "__main__":
    unittest.main()
