"""
Unit tests for etl.parsers.dates, against the format actually observed in
the dump ("28-Jan-2026 12:00 AM") and its edge cases. Extend with any
additional real-string variants found while sampling the Coal India slice
(H6-H18) if the primary format turns out not to be universal.
"""
import unittest
from datetime import date

from etl.parsers.currency import RejectLog
from etl.parsers.dates import parse_date


class TestParseDate(unittest.TestCase):
    def test_primary_format(self):
        self.assertEqual(parse_date("28-Jan-2026 12:00 AM"), date(2026, 1, 28))

    def test_primary_format_pm(self):
        self.assertEqual(parse_date("27-Jan-2026 12:25 PM"), date(2026, 1, 27))

    def test_primary_format_midday(self):
        self.assertEqual(parse_date("11-May-2026 03:00 PM"), date(2026, 5, 11))

    def test_date_only(self):
        self.assertEqual(parse_date("28-Jan-2026"), date(2026, 1, 28))

    def test_iso_format(self):
        self.assertEqual(parse_date("2026-01-28"), date(2026, 1, 28))

    def test_na_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_date("NA", log))
        self.assertEqual(log.rejections[0].reason, "explicit_na")

    def test_empty_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_date("", log))
        self.assertEqual(log.rejections[0].reason, "explicit_na")

    def test_none_input_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_date(None, log))
        self.assertEqual(log.rejections[0].reason, "null_input")

    def test_garbage_rejected(self):
        log = RejectLog()
        self.assertIsNone(parse_date("not a date", log))
        self.assertEqual(log.rejections[0].reason, "unparseable")

    def test_whitespace_padding(self):
        self.assertEqual(parse_date("  28-Jan-2026 12:00 AM  "), date(2026, 1, 28))

    def test_leap_year(self):
        self.assertEqual(parse_date("29-Feb-2024 12:00 AM"), date(2024, 2, 29))


if __name__ == "__main__":
    unittest.main()
