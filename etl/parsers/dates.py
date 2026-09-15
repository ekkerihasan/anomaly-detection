"""
Parses date strings as they appear in the raw CPPP dump. Same rationale as
etl.parsers.currency (CLAUDE.md rule 6): F2/F9/F12 all depend on correct
date arithmetic, so every rejection is logged with a reason instead of
silently becoming None.

Observed format in this dump (aoc_tenders.aoc_date/closing_date,
aoc_details Contract/Published/Award Published Date, tenders_vps
e_published_date/bid_submission_closing_date/tender_opening_date):
"28-Jan-2026 12:00 AM" -- "%d-%b-%Y %I:%M %p".
"""
from datetime import date, datetime
from typing import Optional

from etl.parsers.currency import RejectLog

_EXPLICIT_NA = {"NA", "N/A", "N.A", "N.A.", "NIL", "NONE", "-", "--", ""}

# Order matters: try the exact observed format first.
_FORMATS = [
    "%d-%b-%Y %I:%M %p",
    "%d-%b-%Y",
    "%d-%b-%Y %H:%M",
    "%Y-%m-%d",
]


def parse_date(raw: Optional[str], reject_log: Optional[RejectLog] = None) -> Optional[date]:
    """Returns a date, or None if the value could not be parsed. Every
    None is logged to reject_log with a reason when a log is supplied."""

    def reject(reason: str) -> None:
        if reject_log is not None:
            reject_log.add(raw if raw is not None else "<None>", reason)

    if raw is None:
        reject("null_input")
        return None

    if not isinstance(raw, str):
        reject("non_string_input")
        return None

    text = raw.strip()
    if text.upper() in _EXPLICIT_NA:
        reject("explicit_na")
        return None

    for fmt in _FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    reject("unparseable")
    return None
