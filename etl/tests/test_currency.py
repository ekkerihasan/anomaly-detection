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


class TestParseCurrencyRealDumpStrings(unittest.TestCase):
    """50+ real strings sampled from the Coal India Limited slice
    (aoc_tenders Contract Value, tenders_vps EMD) -- CLAUDE.md rule 6:
    'test against 50 real strings pulled from the dump.' Sampled
    2019-2025, Central/Eastern/Western/South Eastern/Northern/Mahanadi
    Coalfields. None of these were rejected when sampled; this test
    guards against a future change silently breaking that."""

    REAL_CONTRACT_VALUES = [
        "44653", "90173", "107097", "111510", "120709", "148979", "188136",
        "195172", "254652", "406897", "413053", "436600", "487340", "657201",
        "678733", "887242", "934500", "1529280", "1978270", "3020828",
        "4592708", "4759604", "5402925", "5540100", "58787.6", "78791.9",
        "516980.6", "148368.49", "148747.26", "1649321.4", "165095.16",
        "184832.62", "190670.18", "201657.28", "204512.38", "218548.84",
        "309836.82", "3306216.2", "430944.35", "462166.47", "766664.08",
        "790820.65", "870279.22", "953983.55", "995879.87", "1157708.62",
        "1236983.38", "1655316.04", "2006080.24", "2121213.55",
    ]

    REAL_EMD_VALUES = [
        "₹ 1500", "₹ 8100", "₹ 8380", "₹ 8600", "₹ 8937",
        "₹ 9800", "₹ 10000", "₹ 13840", "₹ 15900", "₹ 19000",
        "₹ 19500", "₹ 21000", "₹ 21132", "₹ 28900", "₹ 35900",
        "₹ 49966", "₹ 58600", "₹ 60000", "₹ 60500", "₹ 66000",
        "₹ 70380", "₹ 71100", "₹ 75475", "₹ 80000", "₹ 89000",
        "₹ 90000", "₹ 160000", "₹ 176000", "₹ 255000",
        "₹ 330000", "₹ 383000", "₹ 420000", "₹ 635440",
        "₹ 1037595", "₹ 1384000",
    ]

    def test_no_real_contract_values_rejected(self):
        log = RejectLog()
        failures = [s for s in self.REAL_CONTRACT_VALUES if parse_currency(s, log) is None]
        self.assertEqual(failures, [])

    def test_no_real_emd_values_rejected(self):
        log = RejectLog()
        failures = [s for s in self.REAL_EMD_VALUES if parse_currency(s, log) is None]
        self.assertEqual(failures, [])

    def test_real_emd_value_shape(self):
        self.assertEqual(parse_currency("₹ 10000"), Decimal("10000"))


if __name__ == "__main__":
    unittest.main()
