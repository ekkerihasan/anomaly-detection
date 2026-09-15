"""
Parses currency strings as they appear in the raw CPPP dump into Decimal
rupee amounts.

CLAUDE.md rule 6: values arrive as "1,23,45,678.00", "Rs. 45,00,000", "NA",
"", and sometimes in lakhs/crore. This is the one parser everything else
(F5 threshold bunching, F11 EMD ratio, F1 value-based severity) depends on.
A silent None here silently kills three flags, so every rejection is logged
with a reason instead of being swallowed.
"""
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Optional

_EXPLICIT_NA = {
    "NA", "N/A", "N.A", "N.A.", "NIL", "NONE", "NOT AVAILABLE",
    "-", "--", "TBD", "UNKNOWN", "TO BE DECIDED",
}

_CURRENCY_SYMBOLS = re.compile(r"(?i)\b(rs|inr|rupees?)\.?\s*|₹")

_MULTIPLIERS = {
    "crore": Decimal("10000000"),
    "crores": Decimal("10000000"),
    "cr": Decimal("10000000"),
    "lakh": Decimal("100000"),
    "lakhs": Decimal("100000"),
    "lac": Decimal("100000"),
    "lacs": Decimal("100000"),
    "l": Decimal("100000"),
}

_MULTIPLIER_SUFFIX = re.compile(
    r"(?i)\s*(crores?|cr|lakh?s?|lacs?|l)\s*$"
)

_NUMERIC = re.compile(r"^-?\d+(\.\d+)?$")


@dataclass
class Rejection:
    raw: str
    reason: str


@dataclass
class RejectLog:
    rejections: list = field(default_factory=list)

    def add(self, raw: str, reason: str) -> None:
        self.rejections.append(Rejection(raw=raw, reason=reason))

    def to_rows(self):
        return [{"raw": r.raw, "reason": r.reason} for r in self.rejections]


def parse_currency(raw: Optional[str], reject_log: Optional[RejectLog] = None) -> Optional[Decimal]:
    """Returns a Decimal rupee amount, or None if the value could not be
    parsed as a currency figure. Every None is logged to reject_log with a
    reason when a log is supplied, so ETL can report a coverage figure
    rather than silently dropping rows."""

    def reject(reason: str) -> None:
        if reject_log is not None:
            reject_log.add(raw if raw is not None else "<None>", reason)

    if raw is None:
        reject("null_input")
        return None

    if not isinstance(raw, str):
        # numeric types (already parsed) pass through as Decimal
        try:
            return Decimal(str(raw))
        except (InvalidOperation, ValueError):
            reject("non_string_non_numeric")
            return None

    text = raw.strip()
    if text == "":
        reject("empty")
        return None

    if text.upper() in _EXPLICIT_NA:
        reject("explicit_na")
        return None

    cleaned = _CURRENCY_SYMBOLS.sub("", text).strip()

    # "/-" (and a bare trailing "/") is standard Indian notation for "only",
    # e.g. "Rs.50,000/-" -- strip it before the numeric match.
    cleaned = re.sub(r"/-?\s*$", "", cleaned).strip()

    multiplier = Decimal(1)
    m = _MULTIPLIER_SUFFIX.search(cleaned)
    if m:
        word = m.group(1).lower()
        multiplier = _MULTIPLIERS.get(word, Decimal(1))
        cleaned = cleaned[: m.start()].strip()

    # commas in this data are Indian-style grouping (1,23,45,678) or
    # occasionally Western (1,234,567); either way the digits are the
    # same once every comma is stripped.
    cleaned = cleaned.replace(",", "").strip()

    if cleaned == "":
        reject("no_digits_after_strip")
        return None

    if not _NUMERIC.match(cleaned):
        reject("unparseable")
        return None

    try:
        value = Decimal(cleaned) * multiplier
    except InvalidOperation:
        reject("decimal_conversion_failed")
        return None

    if value < 0:
        reject("negative_value")
        return None

    return value
