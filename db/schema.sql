-- Schema per MHASH26-BUILD-PLAN.md Section 7. Applied by hand (psql -f) —
-- no ORM migration framework per CLAUDE.md rule 8.

CREATE TABLE organisation (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    name_norm   TEXT NOT NULL,
    org_type    TEXT,
    state       TEXT
);

CREATE TABLE vendor (
    id           BIGSERIAL PRIMARY KEY,
    name_raw     TEXT NOT NULL,
    name_norm    TEXT NOT NULL,
    address_raw  TEXT,
    address_norm TEXT
);

CREATE TABLE tender (
    id                BIGSERIAL PRIMARY KEY,
    ref_no            TEXT,
    org_id            BIGINT REFERENCES organisation(id),
    title             TEXT,
    description       TEXT,
    category          TEXT,
    product_category  TEXT,
    tender_type       TEXT,
    epublished_date   DATE,
    bid_start_date    DATE,
    bid_end_date      DATE,
    bid_open_date     DATE,
    emd               NUMERIC,
    tender_fee        NUMERIC,
    detail_url        TEXT
);

CREATE TABLE award (
    id              BIGSERIAL PRIMARY KEY,
    tender_id       BIGINT REFERENCES tender(id),
    vendor_id       BIGINT REFERENCES vendor(id),
    contract_value  NUMERIC,
    contract_date   DATE,
    bids_received   INT,
    completion_days INT,
    detail_url      TEXT
);

-- flag.evidence is the load-bearing column the explanation UI renders
-- from directly. Every flag implementation must populate it.
CREATE TABLE flag (
    id         BIGSERIAL PRIMARY KEY,
    award_id   BIGINT REFERENCES award(id),
    code       TEXT NOT NULL,        -- 'F1_SINGLE_BID'
    severity   NUMERIC NOT NULL,     -- 0..1
    evidence   JSONB NOT NULL,       -- the numbers behind the sentence
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE risk_score (
    award_id    BIGINT PRIMARY KEY REFERENCES award(id),
    score       NUMERIC NOT NULL,
    rank        INT,
    computed_at TIMESTAMP DEFAULT now()
);

CREATE TABLE review (
    award_id   BIGINT PRIMARY KEY REFERENCES award(id),
    status     TEXT NOT NULL DEFAULT 'open',  -- open|reviewing|referred|dismissed
    note       TEXT,
    updated_at TIMESTAMP DEFAULT now()
);

-- Round 2 lands here (post-award subcontractor variations). Created now,
-- left empty in Round 1.
CREATE TABLE contract_variation (
    id            BIGSERIAL PRIMARY KEY,
    award_id      BIGINT REFERENCES award(id),
    variation_no  INT,
    varied_on     DATE,
    value_delta   NUMERIC,
    reason        TEXT,
    subcontractor TEXT
);

CREATE INDEX idx_tender_org_id ON tender(org_id);
CREATE INDEX idx_award_tender_id ON award(tender_id);
CREATE INDEX idx_award_vendor_id ON award(vendor_id);
CREATE INDEX idx_award_contract_date ON award(contract_date);
CREATE INDEX idx_flag_award_id ON flag(award_id);
CREATE INDEX idx_flag_code ON flag(code);
CREATE INDEX idx_vendor_name_norm ON vendor(name_norm);
CREATE INDEX idx_organisation_name_norm ON organisation(name_norm);
