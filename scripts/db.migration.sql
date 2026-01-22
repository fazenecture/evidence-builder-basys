BEGIN;

-- =========================
-- SCHEMAS
-- =========================
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS phi;


-- =========================
-- EXTENSIONS
-- =========================
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- =========================
-- CORE: PA REQUESTS
-- =========================
CREATE TABLE core.pa_requests (
  id            SERIAL PRIMARY KEY,                         -- internal PK
  request_uuid  UUID NOT NULL DEFAULT gen_random_uuid(),    -- external/public ID
  status        VARCHAR(32) NOT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by    VARCHAR(128) NOT NULL,
  modified_by   VARCHAR(128) NOT NULL,
  CONSTRAINT uq_pa_requests_request_uuid UNIQUE (request_uuid)
);

-- =========================
-- CORE: DOCUMENTS
-- =========================
CREATE TABLE core.documents (
  id               SERIAL PRIMARY KEY,
  document_uuid  UUID NOT NULL DEFAULT gen_random_uuid(),    -- external/public ID
  pa_request_id    INTEGER NOT NULL
                     REFERENCES core.pa_requests(id)
                     ON DELETE CASCADE,
  idempotency_key  VARCHAR(255) NOT NULL,
  status           VARCHAR(32) NOT NULL,
  created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at      TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by       VARCHAR(128) NOT NULL,
  modified_by      VARCHAR(128) NOT NULL,
  CONSTRAINT uq_documents_pa_idempotency
    UNIQUE (pa_request_id, idempotency_key)
  CONSTRAINT uq_documents_document_uuid UNIQUE (document_uuid)
);

-- =========================
-- CORE: PROCESSING JOBS
-- =========================
CREATE TABLE core.processing_jobs (
  id             SERIAL PRIMARY KEY,
  job_uuid       UUID NOT NULL UNIQUE,
  document_id    INTEGER NOT NULL
                   REFERENCES core.documents(id)
                   ON DELETE CASCADE,
  status         VARCHAR(32) NOT NULL,
  attempt_count  INTEGER NOT NULL DEFAULT 0,
  last_error     TEXT,
  trace_id       UUID,
  created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at    TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by     VARCHAR(128) NOT NULL,
  modified_by    VARCHAR(128) NOT NULL,
  CONSTRAINT processing_jobs_job_uuid_unique UNIQUE (job_uuid)
);

-- =========================
-- CORE: DEAD LETTER JOBS
-- =========================
CREATE TABLE core.dead_letter_jobs (
  id           SERIAL PRIMARY KEY,
  job_uuid     UUID NOT NULL,
  document_id  INTEGER,
  reason       TEXT NOT NULL,
  payload      JSONB,
  created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at  TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by   VARCHAR(128) NOT NULL,
  modified_by  VARCHAR(128) NOT NULL
);

-- =========================
-- CORE: EVIDENCE PACKS
-- =========================
CREATE TABLE core.evidence_packs (
  id             SERIAL PRIMARY KEY,
  pa_request_id  INTEGER NOT NULL UNIQUE
                   REFERENCES core.pa_requests(id)
                   ON DELETE CASCADE,
  status         VARCHAR(32) NOT NULL DEFAULT 'created',
  decision       VARCHAR(32),
  explanation    TEXT,
  sources        JSONB,
  metadata       JSONB,
  created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at    TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by     VARCHAR(128) NOT NULL,
  modified_by    VARCHAR(128) NOT NULL
);

-- =========================
-- CORE: AUDIT LOGS
-- =========================
CREATE TABLE core.audit_logs (
  id            SERIAL PRIMARY KEY,
  pa_request_id INTEGER
                  REFERENCES core.pa_requests(id)
                  ON DELETE SET NULL,
  actor         VARCHAR(128) NOT NULL,
  action        VARCHAR(64) NOT NULL,
  metadata      JSONB,
  created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by    VARCHAR(128) NOT NULL,
  modified_by   VARCHAR(128) NOT NULL
);

-- =========================
-- PHI: DOCUMENT TEXT
-- =========================
CREATE TABLE phi.document_text (
  id           SERIAL PRIMARY KEY,
  document_id  INTEGER NOT NULL
                 REFERENCES core.documents(id)
                 ON DELETE CASCADE,
  text         TEXT NOT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at  TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by   VARCHAR(128) NOT NULL,
  modified_by  VARCHAR(128) NOT NULL
);

-- =========================
-- PHI: EXTRACTED EVIDENCE
-- =========================
CREATE TABLE phi.extracted_evidence (
  id                    SERIAL PRIMARY KEY,

  evidence_pack_id      INTEGER NOT NULL
                           REFERENCES core.evidence_packs(id)
                           ON DELETE CASCADE,

  diagnosis             VARCHAR(255),
  imaging_present       BOOLEAN,
  therapy_attempted     BOOLEAN,
  functional_limitation BOOLEAN,
  missing_fields        JSONB,
  sources               JSONB,

  created_at            TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at           TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by            VARCHAR(128) NOT NULL,
  modified_by           VARCHAR(128) NOT NULL
);


-- =========================
-- INDEXES
-- =========================
CREATE INDEX idx_documents_pa_request_id
  ON core.documents(pa_request_id);

CREATE INDEX idx_processing_jobs_document_id
  ON core.processing_jobs(document_id);

CREATE INDEX idx_audit_logs_pa_request_id
  ON core.audit_logs(pa_request_id);

CREATE INDEX idx_extracted_evidence_document_id
  ON phi.extracted_evidence(document_id);

COMMIT;
