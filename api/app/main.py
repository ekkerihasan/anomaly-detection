"""FastAPI entrypoint.

All scoring and flag logic is server-side (CLAUDE.md rule 5) -- and in fact
happens upstream of this process entirely, in scripts/compute_flags.py and
scripts/compute_scores.py. These routes read precomputed `flag` and
`risk_score` rows and render them. Nothing here evaluates a threshold.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import get_weights
from app.db import get_cursor
from app.explain import explain

app = FastAPI(title="Procurement Anomaly Detection API")

# Next.js dev server. Round 1 has no auth (plan Section 5, out of scope).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set by scripts/seed_dev.py on every fixture organisation. Its presence is
# how the UI knows to warn that nothing on screen is real (CLAUDE.md rule 10).
DEV_FIXTURE_ORG_TYPE = "DEV_FIXTURE_SYNTHETIC"

VALID_REVIEW_STATUSES = ("open", "reviewing", "referred", "dismissed")


# --------------------------------------------------------------------------
# health / meta
# --------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1 AS ok")
            row = cur.fetchone()
        return {"status": "ok", "db": row}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"database unreachable: {exc}")


@app.get("/config/weights")
def config_weights():
    """Exposes config/weights.yaml verbatim so the frontend/demo can show
    the real thresholds on camera without duplicating them."""
    return get_weights()


@app.get("/meta/dataset")
def meta_dataset():
    """Tells the frontend whether it is looking at the real slice or the dev
    fixture, so a synthetic dataset can never be screenshotted as a finding.

    `synthetic` flips to false on its own once a real slice is loaded --
    there is no flag to remember to unset.
    """
    with get_cursor() as cur:
        cur.execute(
            "SELECT count(*) FILTER (WHERE org_type = %s) AS fixture_orgs, "
            "count(*) AS total_orgs FROM organisation",
            (DEV_FIXTURE_ORG_TYPE,),
        )
        orgs = cur.fetchone()
        cur.execute("SELECT count(*) AS n FROM award")
        awards = cur.fetchone()["n"]
        cur.execute("SELECT count(*) AS n FROM risk_score")
        scored = cur.fetchone()["n"]

    synthetic = orgs["total_orgs"] > 0 and orgs["fixture_orgs"] == orgs["total_orgs"]
    return {
        "synthetic": synthetic,
        "label": (
            "SYNTHETIC DEV FIXTURE - not real procurement data, nothing here is a finding"
            if synthetic else "Live slice"
        ),
        "awards": awards,
        "scored": scored,
    }


# --------------------------------------------------------------------------
# awards
# --------------------------------------------------------------------------

@app.get("/awards")
def list_awards(
    organisation_id: int | None = None,
    flag_code: str | None = None,
    review_status: str | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Ranked list (plan Section 10, screen 1).

    Ordered by precomputed score. Awards with no flags have no risk_score row
    and so never appear -- this is a review queue, not a list of everything.
    """
    if review_status is not None and review_status not in VALID_REVIEW_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"review_status must be one of {list(VALID_REVIEW_STATUSES)}",
        )

    where = []
    params: dict = {"limit": limit, "offset": offset}

    if organisation_id is not None:
        where.append("t.org_id = %(organisation_id)s")
        params["organisation_id"] = organisation_id
    if min_value is not None:
        where.append("a.contract_value >= %(min_value)s")
        params["min_value"] = min_value
    if max_value is not None:
        where.append("a.contract_value <= %(max_value)s")
        params["max_value"] = max_value
    if date_from is not None:
        where.append("a.contract_date >= %(date_from)s")
        params["date_from"] = date_from
    if date_to is not None:
        where.append("a.contract_date <= %(date_to)s")
        params["date_to"] = date_to
    if review_status is not None:
        # 'open' must also match awards with no review row yet.
        if review_status == "open":
            where.append("COALESCE(rv.status, 'open') = 'open'")
        else:
            where.append("rv.status = %(review_status)s")
            params["review_status"] = review_status
    if flag_code is not None:
        where.append(
            "EXISTS (SELECT 1 FROM flag f2 WHERE f2.award_id = a.id "
            "AND f2.code = %(flag_code)s)"
        )
        params["flag_code"] = flag_code

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    sql = f"""
        SELECT a.id,
               rs.score,
               rs.rank,
               o.name  AS organisation,
               o.id    AS organisation_id,
               v.name_raw AS vendor,
               a.contract_value,
               a.contract_date,
               a.detail_url,
               COALESCE(rv.status, 'open') AS review_status,
               ARRAY(SELECT f.code FROM flag f WHERE f.award_id = a.id ORDER BY f.code)
                   AS flag_codes
        FROM risk_score rs
        JOIN award a        ON a.id = rs.award_id
        JOIN tender t       ON t.id = a.tender_id
        LEFT JOIN organisation o ON o.id = t.org_id
        LEFT JOIN vendor v  ON v.id = a.vendor_id
        LEFT JOIN review rv ON rv.award_id = a.id
        {where_sql}
        ORDER BY rs.score DESC, a.id
        LIMIT %(limit)s OFFSET %(offset)s
    """
    count_sql = f"""
        SELECT count(*) AS n
        FROM risk_score rs
        JOIN award a        ON a.id = rs.award_id
        JOIN tender t       ON t.id = a.tender_id
        LEFT JOIN organisation o ON o.id = t.org_id
        LEFT JOIN vendor v  ON v.id = a.vendor_id
        LEFT JOIN review rv ON rv.award_id = a.id
        {where_sql}
    """

    with get_cursor() as cur:
        cur.execute(count_sql, params)
        total = cur.fetchone()["n"]
        cur.execute(sql, params)
        rows = cur.fetchall()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "awards": [
            {
                "id": r["id"],
                "organisation": r["organisation"],
                "organisationId": r["organisation_id"],
                "vendor": r["vendor"],
                "contractValue": float(r["contract_value"]) if r["contract_value"] is not None else None,
                "contractDate": r["contract_date"].isoformat() if r["contract_date"] else None,
                "detailUrl": r["detail_url"],
                "score": float(r["score"]),
                "rank": r["rank"],
                "reviewStatus": r["review_status"],
                "flagCodes": r["flag_codes"],
            }
            for r in rows
        ],
    }


@app.get("/awards/{award_id}")
def get_award(award_id: int):
    """Detail / explanation card (plan Section 10, screen 2).

    Each flag is returned with its raw `evidence` blob *and* the sentence
    built from it, so the UI can show both the prose and the numbers behind
    it without recomputing anything.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT a.id,
                   o.name AS organisation, o.id AS organisation_id,
                   v.name_raw AS vendor,
                   a.contract_value, a.contract_date, a.detail_url,
                   t.title, t.ref_no, t.tender_type,
                   rs.score, rs.rank,
                   COALESCE(rv.status, 'open') AS review_status,
                   rv.note AS review_note
            FROM award a
            JOIN tender t            ON t.id = a.tender_id
            LEFT JOIN organisation o ON o.id = t.org_id
            LEFT JOIN vendor v       ON v.id = a.vendor_id
            LEFT JOIN risk_score rs  ON rs.award_id = a.id
            LEFT JOIN review rv      ON rv.award_id = a.id
            WHERE a.id = %(award_id)s
            """,
            {"award_id": award_id},
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"award {award_id} not found")

        cur.execute(
            "SELECT code, severity, evidence FROM flag WHERE award_id = %(award_id)s "
            "ORDER BY severity DESC, code",
            {"award_id": award_id},
        )
        flag_rows = cur.fetchall()

        cur.execute("SELECT count(*) AS n FROM risk_score")
        total_in_slice = cur.fetchone()["n"]

    flags = []
    for f in flag_rows:
        sentence, citation = explain(f["code"], f["evidence"])
        flags.append({
            "code": f["code"],
            "severity": float(f["severity"]),
            "evidence": f["evidence"],
            "sentence": sentence,
            "ruleCitation": citation,
        })

    return {
        "id": row["id"],
        "organisation": row["organisation"],
        "organisationId": row["organisation_id"],
        "vendor": row["vendor"],
        "title": row["title"],
        "refNo": row["ref_no"],
        "tenderType": row["tender_type"],
        "contractValue": float(row["contract_value"]) if row["contract_value"] is not None else None,
        "contractDate": row["contract_date"].isoformat() if row["contract_date"] else None,
        "detailUrl": row["detail_url"],
        "score": float(row["score"]) if row["score"] is not None else 0.0,
        "rank": row["rank"],
        "totalInSlice": total_in_slice,
        "flags": flags,
        "review": {"status": row["review_status"], "note": row["review_note"]},
    }


class ReviewUpdate(BaseModel):
    status: str = Field(..., description="open|reviewing|referred|dismissed")
    note: str | None = None


@app.put("/awards/{award_id}/review")
def update_review(award_id: int, body: ReviewUpdate):
    """Triage control (plan Section 10). Converts a dashboard into an audit
    tool -- the single cheapest feature on the scoring rubric."""
    if body.status not in VALID_REVIEW_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {list(VALID_REVIEW_STATUSES)}",
        )

    with get_cursor() as cur:
        cur.execute("SELECT 1 FROM award WHERE id = %(award_id)s", {"award_id": award_id})
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail=f"award {award_id} not found")

        cur.execute(
            """
            INSERT INTO review (award_id, status, note, updated_at)
            VALUES (%(award_id)s, %(status)s, %(note)s, now())
            ON CONFLICT (award_id) DO UPDATE
                SET status = EXCLUDED.status,
                    note = EXCLUDED.note,
                    updated_at = now()
            RETURNING status, note, updated_at
            """,
            {"award_id": award_id, "status": body.status, "note": body.note},
        )
        saved = cur.fetchone()

    return {
        "awardId": award_id,
        "status": saved["status"],
        "note": saved["note"],
        "updatedAt": saved["updated_at"].isoformat(),
    }


# --------------------------------------------------------------------------
# organisations
# --------------------------------------------------------------------------

@app.get("/organisations")
def list_organisations():
    """Organisation list, for the ranked-list filter dropdown."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT o.id, o.name, count(a.id) AS award_count
            FROM organisation o
            LEFT JOIN tender t ON t.org_id = o.id
            LEFT JOIN award a  ON a.tender_id = t.id
            GROUP BY o.id, o.name
            ORDER BY o.name
            """
        )
        rows = cur.fetchall()
    return {"organisations": [
        {"id": r["id"], "name": r["name"], "awardCount": r["award_count"]}
        for r in rows
    ]}


@app.get("/organisations/{org_id}/summary")
def organisation_summary(org_id: int):
    """Organisation summary (plan Section 10, screen 3).

    Single-bid rate, concentration by *exact normalised vendor name*, value
    distribution and March clustering. Concentration is deliberately not an
    entity-resolution result -- see the `caveat` field, which the UI renders
    verbatim (CLAUDE.md rule 7).
    """
    # The late-March window must match F12_YEAR_END_RUSH exactly, so it is
    # read from config/weights.yaml (CLAUDE.md rule 4), and the even-spread
    # baseline uses the same arithmetic as scripts/compute_flags.py.
    f12 = get_weights()["flags"]["F12_YEAR_END_RUSH"]
    rush_month, rush_day_from = f12["month"], f12["day_from"]
    days_in_month = 31 if rush_month in (1, 3, 5, 7, 8, 10, 12) else 30
    rush_baseline = (days_in_month - rush_day_from + 1) / 365.0

    with get_cursor() as cur:
        cur.execute("SELECT id, name FROM organisation WHERE id = %(org_id)s",
                    {"org_id": org_id})
        org = cur.fetchone()
        if org is None:
            raise HTTPException(status_code=404, detail=f"organisation {org_id} not found")

        cur.execute(
            """
            SELECT count(*) AS awards,
                   count(*) FILTER (WHERE a.bids_received = 1) AS single_bid,
                   count(*) FILTER (WHERE a.bids_received IS NOT NULL) AS with_bid_data,
                   count(*) FILTER (WHERE EXTRACT(MONTH FROM a.contract_date) = %(rush_month)s
                                      AND EXTRACT(DAY FROM a.contract_date) >= %(rush_day_from)s)
                       AS late_march,
                   count(*) FILTER (WHERE a.contract_date IS NOT NULL) AS with_date,
                   COALESCE(sum(a.contract_value), 0) AS total_value,
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY a.contract_value)
                       AS median_value,
                   max(a.contract_value) AS max_value
            FROM award a
            JOIN tender t ON t.id = a.tender_id
            WHERE t.org_id = %(org_id)s
            """,
            {"org_id": org_id, "rush_month": rush_month, "rush_day_from": rush_day_from},
        )
        stats = cur.fetchone()

        cur.execute(
            """
            SELECT v.name_raw AS vendor,
                   count(*) AS awards,
                   COALESCE(sum(a.contract_value), 0) AS total_value
            FROM award a
            JOIN tender t ON t.id = a.tender_id
            JOIN vendor v ON v.id = a.vendor_id
            WHERE t.org_id = %(org_id)s
            GROUP BY v.name_norm, v.name_raw
            ORDER BY total_value DESC
            LIMIT 10
            """,
            {"org_id": org_id},
        )
        top_vendors = cur.fetchall()

        cur.execute(
            """
            SELECT f.code, count(*) AS n
            FROM flag f
            JOIN award a  ON a.id = f.award_id
            JOIN tender t ON t.id = a.tender_id
            WHERE t.org_id = %(org_id)s
            GROUP BY f.code
            ORDER BY f.code
            """,
            {"org_id": org_id},
        )
        flag_counts = cur.fetchall()

    awards = stats["awards"] or 0
    with_bid_data = stats["with_bid_data"] or 0
    with_date = stats["with_date"] or 0
    total_value = float(stats["total_value"] or 0)

    return {
        "id": org["id"],
        "name": org["name"],
        "awards": awards,
        "singleBidRate": (stats["single_bid"] / with_bid_data) if with_bid_data else None,
        "singleBidCount": stats["single_bid"],
        "lateMarchRate": (stats["late_march"] / with_date) if with_date else None,
        "lateMarchCount": stats["late_march"],
        # Share of the year the rush window covers if awards were spread evenly.
        "lateMarchBaseline": rush_baseline,
        "totalValue": total_value,
        "medianValue": float(stats["median_value"]) if stats["median_value"] is not None else None,
        "maxValue": float(stats["max_value"]) if stats["max_value"] is not None else None,
        "topVendors": [
            {
                "vendor": r["vendor"],
                "awards": r["awards"],
                "totalValue": float(r["total_value"]),
                "shareOfValue": (float(r["total_value"]) / total_value) if total_value else None,
            }
            for r in top_vendors
        ],
        "flagCounts": {r["code"]: r["n"] for r in flag_counts},
        "caveat": (
            "Vendor grouping is normalised exact-name match only, not entity "
            "resolution. Two spellings of the same firm count separately, and a "
            "shared name is a possible relationship for review, not proof of a "
            "single entity."
        ),
    }
