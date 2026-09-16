"""
DEV FIXTURE ONLY -- generates a synthetic slice into the real schema so the
engine, API and UI can be built and verified before the real Coal India
slice is loaded.

This is NOT data, and nothing it produces is a finding. Per CLAUDE.md rule
10 ("never synthesise values to make a screen look complete"), every row
inserted here is marked: `organisation.org_type` is set to the sentinel
DEV_FIXTURE_ORG_TYPE below, which /meta/dataset reads to tell the frontend
to render a persistent "SYNTHETIC DEV DATA" banner. Load the real slice
(scripts/etl_load.py) and the sentinel disappears, and so does the banner.

Vendor names are deliberately fictional. MHASH26-BUILD-PLAN.md Section 14
flags naming a real firm next to the word "risk" as a defamation exposure;
a dev fixture is the last place worth taking that risk.

Distributions are tuned so all six flags fire at plausible rates, including
the messy `tender_type` field documented in docs/h4-data-report.md (the real
dump mixes procurement *category* values with competition *mode* values).
Reproducing that mess here is intentional -- it exercises F1's filter
against the same garbage it will meet in production.

Usage: python scripts/seed_dev.py [--awards N]
"""
import argparse
import os
import random
from datetime import date, timedelta
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

# Read by api/app/main.py:/meta/dataset to drive the synthetic-data banner.
DEV_FIXTURE_ORG_TYPE = "DEV_FIXTURE_SYNTHETIC"

# The six Coal India subsidiaries the real slice covers (docs/h4-data-report.md).
# These are public-sector organisation names, not vendor names.
ORGS = [
    "Central Coalfields Limited",
    "Eastern Coalfields Limited",
    "Western Coalfields Limited",
    "South Eastern Coalfields Limited",
    "Northern Coalfields Limited",
    "Mahanadi Coalfields Limited",
]

# Fictional. Any resemblance to a real contractor is unintended.
VENDOR_STEMS = [
    "Meridian", "Blackstone Ridge", "Corvus", "Ninefold", "Harrow & Sons",
    "Palladium Works", "Stonebridge", "Kestrel", "Ironvale", "Quarrymen",
    "Tarn Valley", "Lodestar", "Ashgrove", "Bellwether", "Crosswind",
    "Drumlin", "Fernhill", "Greyshott", "Hallowfield", "Inchcape",
]
VENDOR_SUFFIXES = ["Constructions Pvt Ltd", "Engineering Works", "Infra Pvt Ltd",
                   "& Co", "Industries Ltd", "Contractors Pvt Ltd"]

# Real dump mixes these two vocabularies in one column -- see h4-data-report.md.
TENDER_TYPES_MODE = ["Open Tender", "Open", "OPEN", "Limited", "LIMITED",
                     "Single", "Nomination"]
TENDER_TYPES_CATEGORY = ["Works", "Goods", "Services"]

CATEGORIES = ["Works", "Goods", "Services"]
PRODUCT_CATEGORIES = [
    "Civil Works", "Electrical Works", "Mining Equipment", "Transport Services",
    "Safety Equipment", "Conveyor Systems", "Building Maintenance", "IT Services",
]
TITLE_VERBS = ["Supply and installation of", "Construction of", "Maintenance of",
               "Procurement of", "Upgradation of", "Hiring of"]
TITLE_NOUNS = ["conveyor belt system", "site electrification", "boundary wall",
               "haul road resurfacing", "workshop shed", "water pipeline",
               "dust suppression units", "weighbridge", "colony quarters",
               "substation equipment"]


def norm(s):
    """Same normalisation shape the ETL uses: casefold + collapse whitespace.
    Exact-match only -- never fuzzy (CLAUDE.md rule 7)."""
    return " ".join(s.lower().split())


def build_rows(n_awards, rng):
    """Generates organisation/vendor/tender/award tuples.

    Flag-bearing rows are injected at controlled rates so every one of the
    six detectors has something to find, and so ranking has a real spread
    rather than a wall of ties.
    """
    vendors = []
    for stem in VENDOR_STEMS:
        for suf in VENDOR_SUFFIXES:
            vendors.append(f"{stem} {suf}")
    rng.shuffle(vendors)

    tenders, awards = [], []
    for i in range(n_awards):
        org_idx = rng.randrange(len(ORGS))
        vendor_idx = rng.randrange(len(vendors))

        # --- baseline (mostly clean) award ----------------------------------
        year = rng.choice([2019, 2020, 2021, 2022, 2023, 2024, 2025])
        epub = date(year, rng.randint(4, 12), rng.randint(1, 28))
        window_days = rng.randint(21, 45)          # compliant by default
        bid_end = epub + timedelta(days=window_days)
        bid_open = bid_end + timedelta(days=rng.randint(0, 3))
        decision_days = rng.randint(7, 60)         # unhurried by default
        contract_date = bid_open + timedelta(days=decision_days)

        # Log-ish value spread: many small awards, a few very large.
        contract_value = round(rng.lognormvariate(13.0, 1.6), 2)
        contract_value = min(contract_value, 900_000_000.0)

        bids_received = rng.choice([2, 3, 3, 4, 4, 5, 6, 7, 9])
        emd = round(contract_value * rng.uniform(0.01, 0.03), 2)

        # Competition mode present on ~70% of rows; the rest carry a
        # *category* value instead, exactly like the real dump.
        if rng.random() < 0.70:
            tender_type = rng.choice(TENDER_TYPES_MODE)
        else:
            tender_type = rng.choice(TENDER_TYPES_CATEGORY)

        # --- inject flag-bearing patterns -----------------------------------
        r = rng.random()

        if r < 0.12:                                    # F1: single bid
            bids_received = 1
            tender_type = rng.choice(["Open Tender", "Open", "OPEN"])
            if rng.random() < 0.45:                     # push some above Rs 50L
                contract_value = round(rng.uniform(5_100_000, 120_000_000), 2)
                emd = round(contract_value * rng.uniform(0.01, 0.03), 2)

        if rng.random() < 0.10:                         # F2: short bid window
            window_days = rng.choice([3, 5, 7, 9, 11, 14, 17, 20])
            bid_end = epub + timedelta(days=window_days)
            bid_open = bid_end + timedelta(days=rng.randint(0, 2))
            contract_date = bid_open + timedelta(days=decision_days)

        if rng.random() < 0.09:                         # F5: threshold bunching
            threshold = rng.choice([5_000_000, 500_000, 50_000])
            # land just under it -- inside 5%, often inside 1%
            pct_below = rng.choice([0.002, 0.004, 0.008, 0.015, 0.03, 0.045])
            contract_value = round(threshold * (1 - pct_below), 2)
            emd = round(contract_value * rng.uniform(0.01, 0.03), 2)

        if rng.random() < 0.08:                         # F9: instant award
            contract_date = bid_open + timedelta(days=rng.choice([0, 0, 1]))

        if rng.random() < 0.05:                         # F11: EMD anomaly
            if rng.random() < 0.5:
                emd = round(contract_value * rng.uniform(0.12, 0.30), 2)  # gatekeeping
            else:
                emd = 0.0                                                # no deterrence

        if rng.random() < 0.11:                         # F12: year-end rush
            fy_end_year = contract_date.year
            contract_date = date(fy_end_year, 3, rng.randint(18, 31))
            # keep the timeline coherent: bidding precedes award
            if bid_open >= contract_date:
                bid_open = contract_date - timedelta(days=rng.randint(1, 30))
                bid_end = bid_open - timedelta(days=rng.randint(0, 2))
                epub = bid_end - timedelta(days=window_days)

        # Guard: never emit a negative-duration timeline.
        if bid_end <= epub:
            bid_end = epub + timedelta(days=max(window_days, 1))
        if bid_open < bid_end:
            bid_open = bid_end
        if contract_date < bid_open:
            contract_date = bid_open

        ref_no = f"{ORGS[org_idx].split()[0][:3].upper()}/{year}/{100000 + i}"
        title = f"{rng.choice(TITLE_VERBS)} {rng.choice(TITLE_NOUNS)}"

        tenders.append((
            ref_no, org_idx, title,
            f"{title} at {ORGS[org_idx]} project site.",
            rng.choice(CATEGORIES), rng.choice(PRODUCT_CATEGORIES), tender_type,
            epub, epub, bid_end, bid_open, emd,
            round(rng.choice([500, 1000, 2000, 5000]), 2),
            f"https://eprocure.gov.in/cppp/tenderdetail/SYNTHETIC-{ref_no}",
        ))
        awards.append((
            vendor_idx, contract_value, contract_date, bids_received,
            rng.choice([90, 180, 270, 365, 540]),
            f"https://eprocure.gov.in/cppp/awarddetail/SYNTHETIC-{ref_no}",
        ))

    return vendors, tenders, awards


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--awards", type=int, default=8000,
                    help="number of synthetic awards to generate (default 8000)")
    ap.add_argument("--seed", type=int, default=20260916,
                    help="RNG seed; fixed so the fixture is reproducible")
    args = ap.parse_args()

    load_dotenv(ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL not set. Copy .env.example to .env and fill it in.")

    rng = random.Random(args.seed)
    vendors, tenders, awards = build_rows(args.awards, rng)

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            # Refuse to run over a real slice. The sentinel org_type is the
            # only thing that distinguishes fixture rows from loaded ones.
            cur.execute("SELECT count(*) FROM organisation WHERE org_type IS DISTINCT FROM %s",
                        (DEV_FIXTURE_ORG_TYPE,))
            real_orgs = cur.fetchone()[0]
            if real_orgs:
                raise SystemExit(
                    f"Refusing to seed: {real_orgs} non-fixture organisation row(s) present. "
                    "This database holds real data -- seed only into an empty or fixture DB."
                )

            print("Clearing existing fixture rows...")
            cur.execute("TRUNCATE contract_variation, review, risk_score, flag, "
                        "award, tender, vendor, organisation RESTART IDENTITY CASCADE")

            print(f"Inserting {len(ORGS)} organisations...")
            org_ids = []
            for name in ORGS:
                cur.execute(
                    "INSERT INTO organisation (name, name_norm, org_type, state) "
                    "VALUES (%s, %s, %s, %s) RETURNING id",
                    (name, norm(name), DEV_FIXTURE_ORG_TYPE, None),
                )
                org_ids.append(cur.fetchone()[0])

            print(f"Inserting {len(vendors)} vendors...")
            vendor_ids = []
            for name in vendors:
                cur.execute(
                    "INSERT INTO vendor (name_raw, name_norm, address_raw, address_norm) "
                    "VALUES (%s, %s, %s, %s) RETURNING id",
                    (name, norm(name), None, None),
                )
                vendor_ids.append(cur.fetchone()[0])

            print(f"Inserting {len(tenders)} tenders and awards...")
            for t, a in zip(tenders, awards):
                (ref_no, org_idx, title, description, category, product_category,
                 tender_type, epub, bid_start, bid_end, bid_open, emd, fee, url) = t
                cur.execute(
                    "INSERT INTO tender (ref_no, org_id, title, description, category, "
                    "product_category, tender_type, epublished_date, bid_start_date, "
                    "bid_end_date, bid_open_date, emd, tender_fee, detail_url) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    (ref_no, org_ids[org_idx], title, description, category,
                     product_category, tender_type, epub, bid_start, bid_end,
                     bid_open, emd, fee, url),
                )
                tender_id = cur.fetchone()[0]

                vendor_idx, contract_value, contract_date, bids, days, aurl = a
                cur.execute(
                    "INSERT INTO award (tender_id, vendor_id, contract_value, "
                    "contract_date, bids_received, completion_days, detail_url) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (tender_id, vendor_ids[vendor_idx], contract_value,
                     contract_date, bids, days, aurl),
                )

        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM award")
            n = cur.fetchone()[0]
        print(f"\nSeeded {n} synthetic awards across {len(ORGS)} organisations.")
        print("*** THIS IS A DEV FIXTURE, NOT DATA. Nothing here is a finding. ***")
        print("Run: python scripts/compute_flags.py")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
