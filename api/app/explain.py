"""
Turns a computed flag + its `evidence` blob into a plain-English sentence
and a rule citation for the explanation card (MHASH26-BUILD-PLAN.md
Section 10).

CLAUDE.md rule 2 permits an LLM *here only* -- rendering an
already-computed flag as prose -- and forbids it anywhere near the score.
We do not use one even here. These are deterministic templates over the
evidence numbers, which means the sentence is reproducible, auditable and
cannot hallucinate a figure that is not in `evidence`. In an audit product
"no model wrote this sentence" is worth more than nicer phrasing.

Every sentence states only numbers that appear in the evidence blob. The
citations are the legal/audit basis recorded in Section 8 of the plan and
must be preserved -- they are part of the product's credibility argument.
"""

# Basis for each flag, per MHASH26-BUILD-PLAN.md Section 8.
RULE_CITATIONS = {
    "F1_SINGLE_BID": "GFR competition principle, OCP red flag 1",
    "F2_SHORT_WINDOW": "GFR 2017 Rule 161",
    "F5_THRESHOLD_BUNCHING": "GFR 2017 Rule 162",
    "F9_INSTANT_AWARD": "OCP red flag, decision period",
    "F11_EMD_ANOMALY": "GFR EMD norms",
    "F12_YEAR_END_RUSH": "Standard audit practice, year-end clustering",
}


# These raise rather than return None on a missing value, so that a builder
# handed an incomplete evidence blob fails into explain()'s honest fallback
# instead of quietly interpolating "None" into an auditor-facing sentence.
# Genuinely optional fields (F1's peer median, F12's shares) are guarded with
# an `is not None` check by the caller before these are ever reached.


def _pct(x, places=1):
    """Renders a 0..1 fraction as a percentage, trimming a trailing .0."""
    if x is None:
        raise ValueError("missing value for percentage")
    v = round(float(x) * 100, places)
    return f"{v:g}%"


def _num(x):
    """Renders a number without a pointless trailing .0."""
    if x is None:
        raise ValueError("missing numeric value")
    f = float(x)
    return f"{int(f)}" if f == int(f) else f"{f:g}"


def _inr_compact(value):
    """Rs 48.1 lakh / Rs 2.3 crore -- the units an Indian auditor reads in."""
    if value is None:
        raise ValueError("missing currency value")
    v = float(value)
    if v >= 10_000_000:
        return f"Rs {v / 10_000_000:.2f} crore".replace(".00 ", " ")
    if v >= 100_000:
        return f"Rs {v / 100_000:.2f} lakh".replace(".00 ", " ")
    return f"Rs {v:,.0f}"


def _f1(e):
    bids = e.get("bids_received")
    peer = e.get("peer_median_bids")
    s = f"Only {_num(bids)} bid was received on a tender advertised as open competition."
    if peer is not None:
        s += (f" Comparable tenders at this organisation received a median of "
              f"{_num(peer)} bids.")
    return s


def _f2(e):
    window = e.get("window_days")
    required = e.get("required_days")
    return (f"The bid submission window was {_num(window)} days. GFR Rule 161 "
            f"requires {_num(required)} days for an advertised tender enquiry.")


def _f5(e):
    gap = e.get("gap_pct")
    threshold = e.get("threshold")
    return (f"The contract value sits {_pct(gap, 2)} below the "
            f"{_inr_compact(threshold)} procedural threshold, just inside the band "
            f"that avoids the next level of procurement scrutiny.")


def _f9(e):
    days = e.get("decision_days")
    peer = e.get("peer_median_days")
    if days is None:
        raise ValueError("decision_days missing")
    if float(days) == 0:
        s = ("The award was made the same day bids were opened, leaving no "
             "measurable evaluation period.")
    else:
        s = (f"The award was made {_num(days)} day after bids were opened, "
             f"leaving effectively no evaluation period.")
    if peer is not None:
        s += (f" Comparable tenders at this organisation took a median of "
              f"{_num(peer)} days.")
    return s


def _f11(e):
    ratio = e.get("ratio")
    median = e.get("peer_ratio_median")
    if ratio is None or median is None:
        raise ValueError("ratio or peer_ratio_median missing")
    if float(ratio) == 0:
        s = ("No earnest money deposit was required on this tender, against a "
             f"median of {_pct(median, 2)} of contract value for this "
             "organisation — little deterrence against a non-serious bid.")
    elif float(ratio) > float(median):
        s = (f"The earnest money deposit is {_pct(ratio, 2)} of the contract "
             f"value, against a {_pct(median, 2)} median for this organisation "
             "— high enough to narrow who can afford to bid.")
    else:
        s = (f"The earnest money deposit is {_pct(ratio, 2)} of the contract "
             f"value, against a {_pct(median, 2)} median for this organisation.")
    return s


def _f12(e):
    march = e.get("org_march_share")
    annual = e.get("org_annual_share")
    s = "This award was made in the last two weeks of March, the close of the financial year."
    if march is not None and annual is not None:
        s += (f" This organisation makes {_pct(march)} of its annual awards in "
              f"that window, against {_pct(annual)} if awards were spread evenly "
              f"across the year.")
    return s


_BUILDERS = {
    "F1_SINGLE_BID": _f1,
    "F2_SHORT_WINDOW": _f2,
    "F5_THRESHOLD_BUNCHING": _f5,
    "F9_INSTANT_AWARD": _f9,
    "F11_EMD_ANOMALY": _f11,
    "F12_YEAR_END_RUSH": _f12,
}


def explain(code, evidence):
    """Returns (sentence, rule_citation) for one flag.

    Falls back to a neutral sentence rather than raising if an unknown code
    appears -- a missing template should not take down the detail page.
    """
    evidence = evidence or {}
    builder = _BUILDERS.get(code)
    citation = RULE_CITATIONS.get(code, "")
    if builder is None:
        return (f"Flag {code} was raised on this award.", citation)
    try:
        return (builder(evidence), citation)
    except (TypeError, ValueError, KeyError):
        # Evidence blob missing a field the template needs. Say so plainly
        # rather than rendering a half-built sentence with a None in it.
        return (f"Flag {code} was raised, but its evidence is incomplete.", citation)
