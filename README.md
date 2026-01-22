# Prior Authorization Processing System

## Overview

This project implements a Prior Authorization processing system that ingests clinical documents, extracts structured medical evidence, evaluates a simplified medical policy, and produces an auditable Evidence Pack.

The system mirrors a real world healthcare workflow and emphasizes correctness, auditability, idempotency, and reliability under failure.

Document ingestion is synchronous. Evidence extraction and policy evaluation are handled asynchronously using a background worker.

## High Level Architecture

The system consists of three core components.

The API service is built using Node.js and TypeScript. It validates requests, enforces idempotency, ingests documents, and exposes read APIs.

A Redis backed queue decouples ingestion from processing. It enables retries, failure isolation, and backpressure handling.

A Python worker service consumes jobs from Redis. It performs evidence extraction, evaluates medical policy rules, generates Evidence Packs, updates workflow state, and writes audit logs.

PostgreSQL is the system of record for workflow state, audit logs, and protected health information.

![alt text](image.png)

## Domain Driven Architecture

The codebase follows a domain driven architecture with clear ownership boundaries.



### PA Requests Domain

This domain manages the lifecycle of a prior authorization request.
It handles request creation, status transitions, and read APIs.
It does not interact with protected health information.

### Documents Domain

This domain manages document ingestion.

It enforces idempotency, persists document metadata, stores document text, and dispatches processing jobs to the queue.

### Worker Domain

The worker domain performs evidence extraction and policy evaluation.

It is responsible for retries, dead letter handling, Evidence Pack creation, and audit logging.

Each domain owns its controllers, services, repositories, and types.

Controllers are thin. Services contain business logic. Database access is isolated in repository layers.

## Database Design

The database is split into two schemas.

The core schema stores workflow and control data such as PA requests, documents, processing jobs, Evidence Packs, dead letter jobs, and audit logs.

The phi schema stores protected health information such as document text and extracted evidence.

Externally exposed identifiers are UUIDs.

Internally, integer primary keys are used for relational integrity.

Strong uniqueness constraints enforce idempotency and system invariants.

A strict one to one relationship exists between PA requests and Evidence Packs.

## Database Schema

```sql
BEGIN;

CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS phi;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE core.pa_requests (
  id SERIAL PRIMARY KEY,
  request_uuid UUID NOT NULL DEFAULT gen_random_uuid(),
  status VARCHAR(32) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by VARCHAR(128) NOT NULL,
  modified_by VARCHAR(128) NOT NULL,
  CONSTRAINT uq_pa_requests_request_uuid UNIQUE (request_uuid)
);

CREATE TABLE core.documents (
  id SERIAL PRIMARY KEY,
  document_uuid UUID NOT NULL DEFAULT gen_random_uuid(),
  pa_request_id INTEGER NOT NULL REFERENCES core.pa_requests(id) ON DELETE CASCADE,
  idempotency_key VARCHAR(255) NOT NULL,
  status VARCHAR(32) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by VARCHAR(128) NOT NULL,
  modified_by VARCHAR(128) NOT NULL,
  CONSTRAINT uq_documents_pa_idempotency UNIQUE (pa_request_id, idempotency_key),
  CONSTRAINT uq_documents_document_uuid UNIQUE (document_uuid)
);

CREATE TABLE core.processing_jobs (
  id SERIAL PRIMARY KEY,
  job_uuid UUID NOT NULL UNIQUE,
  document_id INTEGER NOT NULL REFERENCES core.documents(id) ON DELETE CASCADE,
  status VARCHAR(32) NOT NULL,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  trace_id UUID,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by VARCHAR(128) NOT NULL,
  modified_by VARCHAR(128) NOT NULL
);

CREATE TABLE core.dead_letter_jobs (
  id SERIAL PRIMARY KEY,
  job_uuid UUID NOT NULL,
  document_id INTEGER,
  reason TEXT NOT NULL,
  payload JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by VARCHAR(128) NOT NULL,
  modified_by VARCHAR(128) NOT NULL
);

CREATE TABLE core.evidence_packs (
  id SERIAL PRIMARY KEY,
  pa_request_id INTEGER NOT NULL UNIQUE REFERENCES core.pa_requests(id) ON DELETE CASCADE,
  status VARCHAR(32) NOT NULL DEFAULT 'created',
  decision VARCHAR(32),
  explanation TEXT,
  sources JSONB,
  metadata JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by VARCHAR(128) NOT NULL,
  modified_by VARCHAR(128) NOT NULL
);

CREATE TABLE core.audit_logs (
  id SERIAL PRIMARY KEY,
  pa_request_id INTEGER REFERENCES core.pa_requests(id) ON DELETE SET NULL,
  actor VARCHAR(128) NOT NULL,
  action VARCHAR(64) NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by VARCHAR(128) NOT NULL,
  modified_by VARCHAR(128) NOT NULL
);

CREATE TABLE phi.document_text (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES core.documents(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by VARCHAR(128) NOT NULL,
  modified_by VARCHAR(128) NOT NULL
);

CREATE TABLE phi.extracted_evidence (
  id SERIAL PRIMARY KEY,
  evidence_pack_id INTEGER NOT NULL REFERENCES core.evidence_packs(id) ON DELETE CASCADE,
  diagnosis VARCHAR(255),
  imaging_present BOOLEAN,
  therapy_attempted BOOLEAN,
  functional_limitation BOOLEAN,
  missing_fields JSONB,
  sources JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  modified_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by VARCHAR(128) NOT NULL,
  modified_by VARCHAR(128) NOT NULL
);

COMMIT;


## API Endpoints and Requests

### Create PA Request

Creates a new Prior Authorization request.

```bash
curl -X POST http://localhost:4000/api/v1/pa-requests\
  -H "x-api-key: test-key"
```

### Upload Document

Uploads a clinical document for a PA request.

The Idempotency Key ensures duplicate uploads are safely ignored.

```bash
curl -X POST http://localhost:4000/api/v1/documents/pa-requests/{request_uuid} \
  -H "x-api-key: test-key" \
  -H "Idempotency-Key: doc-001" \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "Patient has severe knee osteoarthritis..."
  }'
```

### Get PA Request Status

Returns the current request status and the latest Evidence Pack summary.

```bash
curl http://localhost:4000/api/v1/pa-requests/{request_uuid}
```

### Get Audit Logs

Returns the audit trail for a PA request.

Audit responses never include protected health information.

```bash
curl http://localhost:4000/api/v1/audit?request_uuid={request_uuid}
```

## Processing Flow

A document upload stores metadata and document text.

A processing job is enqueued in Redis.

The worker consumes the job and tracks attempts in processing_jobs.

Evidence is extracted and policy rules are evaluated.

An Evidence Pack is generated.

PA request status is updated.

Audit logs are written for all major state transitions.

## Retry and Dead Letter Handling

Processing failures are retried up to a configured maximum.

Retryable failures are requeued with incremented attempt counts.

Once retries are exhausted, the job is sent to a dead letter queue.

Dead letter jobs are persisted for investigation and auditing.

## Security and PHI Handling

Protected health information is isolated in the phi schema.

Sensitive data is never returned from audit APIs.

In production, PHI fields should be encrypted at rest using envelope encryption.

## Logging Monitoring and Observability

### What Exists

Structured logs in API and worker services.

Audit logs stored in the database.

Trace IDs associated with processing jobs.

### What Was Omitted Due to Time Constraints

Centralized log aggregation systems.

Automated alerting pipelines.

Distributed tracing dashboards.

These were intentionally omitted to focus on correctness and core system design.

## What Can Be Improved Further

### Reduce Database Calls

Batch audit log writes.

Collapse multiple status updates into single transactions.

Use RETURNING clauses to avoid follow up queries.

### Introduce Caching Layer

Cache PA request status.

Cache processing job state.

Use Redis as a read through cache and short lived state store.

This reduces read load on PostgreSQL.

### PHI Encryption

Encrypt document_text and extracted_evidence columns.

Use envelope encryption with KMS managed keys.

This enables zero trust database access.

### Worker as Independent Microservice

Deploy the worker independently.

Autoscale based on queue depth.

Allow independent release cycles.

### Enhanced ETL and NLP Pipeline

Current extraction is deterministic.

Future improvements include multi stage ETL pipelines.

LLM based extraction with guardrails.

Confidence scoring and provenance tracking.

This enables AI readiness without redesign.

## Secure Document Handling Design Note

This assignment stores document text directly for simplicity.

In production systems, documents should be stored in object storage.

Access should be via pre signed URLs.

The API should never expose bucket paths.

The worker should fetch documents only when required.

This prevents bucket wide access leaks, accidental PHI exposure, and long lived credentials.

## Running Locally

```bash
docker-compose up -d --build
```

The API runs on port 4000.

PostgreSQL and Redis are started automatically.

## Summary

This system models a realistic prior authorization workflow with strong emphasis on auditability, reliability, and correctness.

The architecture is intentionally simple yet extensible, allowing future enhancements without major redesign.
