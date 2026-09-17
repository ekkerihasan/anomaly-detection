"""Tests for the flag -> sentence templates.

The failure mode these guard against is quiet: a template that renders
"None" or "nan%" into an auditor-facing sentence still returns a string, so
nothing raises and the page still loads -- it just shows a number that does
not exist. Every test below asserts on the rendered text.
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.explain import explain, RULE_CITATIONS  # noqa: E402

ALL_CODES = [
    "F1_SINGLE_BID",
    "F2_SHORT_WINDOW",
    "F5_THRESHOLD_BUNCHING",
    "F9_INSTANT_AWARD",
    "F11_EMD_ANOMALY",
    "F12_YEAR_END_RUSH",
]

# Evidence blobs in the exact shape scripts/compute_flags.py writes.
REAL_EVIDENCE = {
    "F1_SINGLE_BID": {"bids_received": 1, "tender_type": "Open", "peer_median_bids": 3.0},
    "F2_SHORT_WINDOW": {"window_days": 9, "required_days": 21,
                        "epublished_date": "2024-03-10", "bid_end_date": "2024-03-19"},
    "F5_THRESHOLD_BUNCHING": {"contract_value": 4811183.17, "threshold": 5000000,
                              "gap_pct": 0.0378,
                              "rule": "GFR Rule 162 - limited tender enquiry up to Rs 50 lakh"},
    "F9_INSTANT_AWARD": {"decision_days": 0, "bid_open_date": "2024-12-13",
                         "contract_date": "2024-12-13", "peer_median_days": 30.0},
    "F11_EMD_ANOMALY": {"emd": 0.0, "contract_value": 113185457.42, "ratio": 0.0,
                        "peer_ratio_median": 0.0202},
    "F12_YEAR_END_RUSH": {"contract_date": "2020-03-24", "org_march_share": 0.1065,
                          "org_annual_share": 0.0384},
}


@pytest.mark.parametrize("code", ALL_CODES)
def test_every_flag_has_a_template_and_a_citation(code):
    sentence, citation = explain(code, REAL_EVIDENCE[code])
    assert sentence and sentence[0].isupper(), f"{code}: sentence not a sentence"
    assert sentence.rstrip().endswith("."), f"{code}: sentence not terminated"
    expected = REAL_EVIDENCE[code].get("rule") or RULE_CITATIONS[code]
    assert citation == expected


@pytest.mark.parametrize("code", ALL_CODES)
def test_no_placeholder_leaks_into_prose(code):
    """The bug class: a missing or unformatted value rendering as text."""
    sentence, _ = explain(code, REAL_EVIDENCE[code])
    # Word-boundary matching: "financial" legitimately contains "nan", and
    # a plain substring check would make this assertion unfalsifiable.
    for leak in ("None", "nan", "inf"):
        pattern = r"\b" + re.escape(leak) + r"\b"
        assert not re.search(pattern, sentence), (
            f"{code}: rendered {leak!r} -> {sentence!r}"
        )
    for leak in ("{", "}", "%s"):
        assert leak not in sentence, f"{code}: rendered {leak!r} -> {sentence!r}"


@pytest.mark.parametrize("code", ALL_CODES)
def test_missing_evidence_degrades_honestly(code):
    """An incomplete blob must say so, not render a half-built sentence."""
    sentence, citation = explain(code, {})
    assert "None" not in sentence
    assert citation == RULE_CITATIONS[code]


def test_unknown_code_does_not_raise():
    sentence, citation = explain("F99_NOT_A_FLAG", {"anything": 1})
    assert "F99_NOT_A_FLAG" in sentence
    assert citation == ""


def test_evidence_none_does_not_raise():
    sentence, _ = explain("F1_SINGLE_BID", None)
    assert isinstance(sentence, str) and sentence


def test_f1_states_the_actual_bid_count_and_peer_median():
    sentence, _ = explain("F1_SINGLE_BID", REAL_EVIDENCE["F1_SINGLE_BID"])
    assert "1 bid" in sentence
    assert "3 bids" in sentence, "peer median should render without a trailing .0"


def test_f2_states_both_the_window_and_the_rule_minimum():
    sentence, _ = explain("F2_SHORT_WINDOW", REAL_EVIDENCE["F2_SHORT_WINDOW"])
    assert "9 days" in sentence
    assert "21 days" in sentence


def test_f5_renders_threshold_in_lakh_not_raw_rupees():
    sentence, _ = explain("F5_THRESHOLD_BUNCHING", REAL_EVIDENCE["F5_THRESHOLD_BUNCHING"])
    assert "lakh" in sentence, "Indian auditors read lakh/crore, not 5000000"
    assert "3.78%" in sentence


@pytest.mark.parametrize("threshold, rule, rule_no", [
    (500000, "GFR Rule 155 - purchase committee Rs 50,000 to Rs 5 lakh", "155"),
    (50000, "GFR Rule 154 - without quotation up to Rs 50,000", "154"),
])
def test_f5_cites_the_rule_for_the_threshold_that_fired(threshold, rule, rule_no):
    """F5 spans three GFR rules; citing Rule 162 under a Rs 50,000 threshold
    would put a wrong legal reference on the explanation card."""
    evidence = {"contract_value": threshold * 0.99, "threshold": threshold,
                "gap_pct": 0.01, "rule": rule}
    _, citation = explain("F5_THRESHOLD_BUNCHING", evidence)
    assert rule_no in citation
    assert "162" not in citation


def test_f9_zero_days_reads_as_same_day():
    sentence, _ = explain("F9_INSTANT_AWARD", REAL_EVIDENCE["F9_INSTANT_AWARD"])
    assert "same day" in sentence
    assert "30 days" in sentence


def test_f9_one_day_does_not_claim_same_day():
    evidence = dict(REAL_EVIDENCE["F9_INSTANT_AWARD"], decision_days=1)
    sentence, _ = explain("F9_INSTANT_AWARD", evidence)
    assert "same day" not in sentence
    assert "1 day" in sentence


def test_f11_zero_emd_reads_as_no_deposit_not_zero_percent():
    sentence, _ = explain("F11_EMD_ANOMALY", REAL_EVIDENCE["F11_EMD_ANOMALY"])
    assert "No earnest money deposit" in sentence


def test_f11_high_emd_reads_as_gatekeeping():
    evidence = dict(REAL_EVIDENCE["F11_EMD_ANOMALY"], ratio=0.10, emd=1000.0)
    sentence, _ = explain("F11_EMD_ANOMALY", evidence)
    assert "10%" in sentence
    assert "narrow who can afford to bid" in sentence


def test_f12_contrasts_march_share_against_even_spread():
    sentence, _ = explain("F12_YEAR_END_RUSH", REAL_EVIDENCE["F12_YEAR_END_RUSH"])
    assert "10.7%" in sentence
    assert "3.8%" in sentence


def test_sentences_never_claim_wrongdoing():
    """Rule 7 / Section 10: the product ranks and explains, it does not accuse."""
    forbidden = ("fraud", "corrupt", "illegal", "guilty", "cartel", "collusion",
                 "rigged", "same entity")
    for code in ALL_CODES:
        sentence, _ = explain(code, REAL_EVIDENCE[code])
        lowered = sentence.lower()
        for word in forbidden:
            assert word not in lowered, f"{code} claims wrongdoing: {sentence!r}"
