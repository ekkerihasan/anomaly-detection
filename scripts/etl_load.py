"""
Loads the chosen slice (Coal India Limited's six subsidiaries, 2019-2025 --
see docs/h4-data-report.md for how this was decided) from the verified
SQLite mirrors into Postgres.

Award-side source: data/raw/aoc_tenders.db (aoc_tenders + aoc_details).
Notice-side source: data/raw/tenders_vps.db (tenders + tender_details),
joined via the base64-decoded tender_id embedded in the notice's
detail_url -- NOT tenders_vps.tenders.tender_id, which is an unrelated
internal scraper id. See docs/h4-data-report.md for how this key was
found and verified (~98.8% join rate for this slice).

Every currency/date value goes through etl/parsers/{currency,dates}.py so
rejections are logged instead of silently becoming NULL (CLAUDE.md rule 6).

Usage: python scripts/etl_load.py
"""
import base64
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from etl.parsers.currency import RejectLog, parse_currency  # noqa: E402
from etl.parsers.dates import parse_date  # noqa: E402

ORGS = [
    "Central Coalfields",
    "Eastern Coalfields",
    "Western Coalfields",
    "South Eastern Coalfields",
    "Northern Coalfields",
    "Mahanadi Coalfields",
]
YEAR_FROM = 2019
YEAR_TO = 2025
BATCH_SIZE = 3000


def normalize_name(s):
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s).strip().upper()
    s = re.sub(r"[.,]+$", "", s)
    return s


def base_tender_id(tid):
    return re.sub(r"_\d+$", "", tid) if tid else tid


def extract_notice_tender_id(detail_url):
    if not detail_url:
        return None
    last = detail_url.rstrip("/").split("A13h1")[-1]
    try:
        return base64.b64decode(last + "==").decode("utf-8", errors="ignore")
    except Exception:
        return None


def load_notice_lookup(vps_conn):
    """Returns {base_tender_id: notice_dict} for the target orgs, built
    from tenders_vps (tenders + tender_details)."""
    cur = vps_conn.cursor()
    cur.row_factory = sqlite3.Row
    like_clause = " OR ".join(["organisation_name LIKE ?"] * len(ORGS))
    params = [o + "%" for o in ORGS]
    cur.execute(
        f"""
        SELECT t.internal_id, t.detail_url, t.reference_number, t.title,
               t.e_published_date, t.bid_submission_closing_date,
               t.tender_opening_date, d.details_json
        FROM tenders t
        LEFT JOIN tender_details d ON d.internal_id = t.internal_id
        WHERE {like_clause}
        """,
        params,
    )
    lookup = {}
    for row in cur.fetchall():
        tid = extract_notice_tender_id(row["detail_url"])
        if not tid:
            continue
        bid = base_tender_id(tid)
        details = {}
        if row["details_json"]:
            try:
                details = json.loads(row["details_json"])
            except json.JSONDecodeError:
                details = {}
        emd_raw = details.get("EMD *") or details.get("EMD")
        fee_raw = details.get("Tender Fee *") or details.get("Tender Fee")
        lookup[bid] = {
            "ref_no": row["reference_number"] or details.get("Tender Reference Number"),
            "title": row["title"] or details.get("Tender Title"),
            "description": details.get("Work Description"),
            "category": details.get("Tender Category"),
            "product_category": details.get("Product Category"),
            "tender_type": details.get("Tender Type"),
            "epublished_date_raw": row["e_published_date"] or details.get("ePublished Date"),
            "bid_start_date_raw": details.get("Bid Submission Start Date"),
            "bid_end_date_raw": row["bid_submission_closing_date"] or details.get("Bid Submission End Date"),
            "bid_open_date_raw": row["tender_opening_date"] or details.get("Bid Opening Date"),
            "emd_raw": emd_raw,
            "tender_fee_raw": fee_raw,
            "detail_url": row["detail_url"],
        }
    return lookup


def main():
    load_dotenv(ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL not set.")

    aoc_conn = sqlite3.connect(f"file:{ROOT}/data/raw/aoc_tenders.db?mode=ro", uri=True)
    aoc_conn.row_factory = sqlite3.Row
    vps_conn = sqlite3.connect(f"file:{ROOT}/data/raw/tenders_vps.db?mode=ro", uri=True)

    print("Building notice-side lookup (tenders_vps)...")
    notice_lookup = load_notice_lookup(vps_conn)
    print(f"  {len(notice_lookup):,} notice records indexed by base tender_id")

    currency_rejects = RejectLog()
    date_rejects = RejectLog()

    orgs = {}       # name_norm -> {name, ...}
    vendors = {}     # name_norm -> {name_raw, address_raw, address_norm}
    tenders = {}     # base_tender_id -> tender dict (org_name_norm resolved later)
    awards = []      # list of award dicts (org_name_norm, vendor_name_norm, base_tender_id, ...)

    print("Reading award-side (aoc_tenders + aoc_details)...")
    like_clause = " OR ".join(["t.org_name LIKE ?"] * len(ORGS))
    params = [o + "%" for o in ORGS]
    cur = aoc_conn.cursor()
    cur.execute(
        f"""
        SELECT t.tender_id, t.org_name, d.details_json
        FROM aoc_tenders t
        JOIN aoc_details d ON d.internal_id = t.internal_id
        WHERE ({like_clause}) AND t.year BETWEEN ? AND ?
        """,
        params + [YEAR_FROM, YEAR_TO],
    )

    n = 0
    for row in cur:
        n += 1
        if n % 20000 == 0:
            print(f"  ...{n:,} award rows processed")

        full_tid = row["tender_id"]
        bid = base_tender_id(full_tid)
        org_name = row["org_name"]
        try:
            details = json.loads(row["details_json"])
        except json.JSONDecodeError:
            continue

        org_norm = normalize_name(org_name)
        if org_norm and org_norm not in orgs:
            orgs[org_norm] = {"name": org_name, "org_type": "PSU", "state": None}

        vendor_raw = details.get("Name of the selected bidder(s)")
        address_raw = details.get("Address of the selected bidder(s)")
        vendor_norm = normalize_name(vendor_raw) if vendor_raw else None
        if vendor_norm and vendor_norm not in vendors:
            vendors[vendor_norm] = {
                "name_raw": vendor_raw,
                "address_raw": address_raw,
                "address_norm": normalize_name(address_raw) if address_raw else None,
            }

        notice = notice_lookup.get(bid, {})

        if bid not in tenders:
            ref_no = notice.get("ref_no") or details.get("Tender Ref. No.")
            tender_type = notice.get("tender_type") or details.get("Tender Type")
            epub_raw = notice.get("epublished_date_raw") or details.get("Published Date") or details.get("Award Published Date")
            tenders[bid] = {
                "ref_no": ref_no,
                "org_norm": org_norm,
                "title": notice.get("title") or details.get("Tender Description"),
                "description": notice.get("description") or details.get("Tender Description"),
                "category": notice.get("category"),
                "product_category": notice.get("product_category"),
                "tender_type": tender_type,
                "epublished_date": parse_date(epub_raw, date_rejects) if epub_raw else None,
                "bid_start_date": parse_date(notice.get("bid_start_date_raw"), date_rejects) if notice.get("bid_start_date_raw") else None,
                "bid_end_date": parse_date(notice.get("bid_end_date_raw"), date_rejects) if notice.get("bid_end_date_raw") else None,
                "bid_open_date": parse_date(notice.get("bid_open_date_raw"), date_rejects) if notice.get("bid_open_date_raw") else None,
                "emd": parse_currency(notice.get("emd_raw"), currency_rejects) if notice.get("emd_raw") else None,
                "tender_fee": parse_currency(notice.get("tender_fee_raw"), currency_rejects) if notice.get("tender_fee_raw") else None,
                "detail_url": notice.get("detail_url"),
            }

        bids_received_raw = details.get("Number of bids received")
        bids_received = None
        if bids_received_raw not in (None, "", "NA", "N/A"):
            try:
                bids_received = int(str(bids_received_raw).strip())
            except ValueError:
                pass

        awards.append({
            "base_tender_id": bid,
            "vendor_norm": vendor_norm,
            "contract_value": parse_currency(details.get("Contract Value"), currency_rejects),
            "contract_date": parse_date(details.get("Contract Date"), date_rejects) if details.get("Contract Date") else None,
            "bids_received": bids_received,
            "completion_days": None,
            "detail_url": details.get("Tender Document"),
        })

    print(f"Parsed {n:,} award rows -> {len(orgs):,} organisations, "
          f"{len(vendors):,} vendors, {len(tenders):,} tenders, {len(awards):,} awards")
    print(f"Currency rejects: {len(currency_rejects.rejections):,}")
    print(f"Date rejects: {len(date_rejects.rejections):,}")

    print("Connecting to Postgres...")
    pg = psycopg2.connect(database_url)
    pg.autocommit = False
    pcur = pg.cursor()

    print("Inserting organisations...")
    org_ids = {}
    org_items = list(orgs.items())
    for i in range(0, len(org_items), BATCH_SIZE):
        batch = org_items[i:i + BATCH_SIZE]
        rows = [(v["name"], k, v["org_type"], v["state"]) for k, v in batch]
        result = psycopg2.extras.execute_values(
            pcur,
            "INSERT INTO organisation (name, name_norm, org_type, state) VALUES %s RETURNING id",
            rows,
            fetch=True,
        )
        for (norm_key, _), (new_id,) in zip(batch, result):
            org_ids[norm_key] = new_id
    pg.commit()
    print(f"  {len(org_ids):,} organisations inserted")

    print("Inserting vendors...")
    vendor_ids = {}
    vendor_items = list(vendors.items())
    for i in range(0, len(vendor_items), BATCH_SIZE):
        batch = vendor_items[i:i + BATCH_SIZE]
        rows = [(v["name_raw"], k, v["address_raw"], v["address_norm"]) for k, v in batch]
        result = psycopg2.extras.execute_values(
            pcur,
            "INSERT INTO vendor (name_raw, name_norm, address_raw, address_norm) VALUES %s RETURNING id",
            rows,
            fetch=True,
        )
        for (norm_key, _), (new_id,) in zip(batch, result):
            vendor_ids[norm_key] = new_id
    pg.commit()
    print(f"  {len(vendor_ids):,} vendors inserted")

    print("Inserting tenders...")
    tender_ids = {}
    tender_items = list(tenders.items())
    for i in range(0, len(tender_items), BATCH_SIZE):
        batch = tender_items[i:i + BATCH_SIZE]
        rows = [
            (
                v["ref_no"], org_ids.get(v["org_norm"]), v["title"], v["description"],
                v["category"], v["product_category"], v["tender_type"],
                v["epublished_date"], v["bid_start_date"], v["bid_end_date"], v["bid_open_date"],
                v["emd"], v["tender_fee"], v["detail_url"],
            )
            for _, v in batch
        ]
        result = psycopg2.extras.execute_values(
            pcur,
            """INSERT INTO tender (ref_no, org_id, title, description, category,
               product_category, tender_type, epublished_date, bid_start_date,
               bid_end_date, bid_open_date, emd, tender_fee, detail_url)
               VALUES %s RETURNING id""",
            rows,
            fetch=True,
        )
        for (base_id, _), (new_id,) in zip(batch, result):
            tender_ids[base_id] = new_id
    pg.commit()
    print(f"  {len(tender_ids):,} tenders inserted")

    print("Inserting awards...")
    inserted_awards = 0
    for i in range(0, len(awards), BATCH_SIZE):
        batch = awards[i:i + BATCH_SIZE]
        rows = [
            (
                tender_ids.get(a["base_tender_id"]),
                vendor_ids.get(a["vendor_norm"]) if a["vendor_norm"] else None,
                a["contract_value"], a["contract_date"], a["bids_received"],
                a["completion_days"], a["detail_url"],
            )
            for a in batch
        ]
        psycopg2.extras.execute_values(
            pcur,
            """INSERT INTO award (tender_id, vendor_id, contract_value, contract_date,
               bids_received, completion_days, detail_url) VALUES %s""",
            rows,
        )
        inserted_awards += len(batch)
    pg.commit()
    print(f"  {inserted_awards:,} awards inserted")

    reject_path = ROOT / "docs" / "etl-reject-report.md"
    with open(reject_path, "w", encoding="utf-8") as f:
        f.write("# ETL reject report\n\n")
        f.write(f"Slice: {', '.join(ORGS)}, {YEAR_FROM}-{YEAR_TO}\n\n")
        f.write(f"Award rows processed: {n:,}\n\n")
        f.write(f"## Currency parse rejects: {len(currency_rejects.rejections):,}\n\n")
        from collections import Counter
        reasons = Counter(r.reason for r in currency_rejects.rejections)
        for reason, count in reasons.most_common():
            f.write(f"- `{reason}`: {count:,}\n")
        f.write(f"\n## Date parse rejects: {len(date_rejects.rejections):,}\n\n")
        reasons = Counter(r.reason for r in date_rejects.rejections)
        for reason, count in reasons.most_common():
            f.write(f"- `{reason}`: {count:,}\n")
    print(f"Reject report written to {reject_path}")

    pg.close()
    print("Done.")


if __name__ == "__main__":
    main()
