# EvidenceBridge — Architecture

**Version:** 0.1.0
**Status:** Hackathon MVP

## 1. Architecture Goal

Build a small, modular evidence-verification system where probabilistic AI is used for extraction, planning, and synthesis, while deterministic application code owns normalization, comparison, validation, and output contracts.

## 2. High-Level Architecture

```text
User
  |
  v
DronaHQ UI
  |
  v
Trust/Verification Agent
  |-----------------------------|
  v                             v
FastAPI Service               Anakin
  |                             |
  |-- PDF extraction            |-- Web search/research
  |-- claim normalization       |-- Source metadata
  |-- comparison                |-- snippets/evidence
  |-- report schema             |
  |-----------------------------|
                |
                v
         Evidence Model
                |
                v
         Verification Report
                |
                v
      Verification Request

             Nasiko
        deployment/runtime layer
```

## 3. Component Responsibilities

### 3.1 DronaHQ

Responsibilities:
- Main user experience
- Input forms
- File submission workflow
- Agent invocation
- Progress/status presentation
- Final report presentation

DronaHQ is an orchestration/application layer, not the place for all business logic.

### 3.2 Verification Agent

Responsibilities:
- Interpret the verification request
- Determine which research steps are needed
- Invoke approved tools
- Summarize evidence
- Produce a structured report

The agent must not invent source facts and must follow the output schema.

### 3.3 FastAPI Backend

Suggested modules:

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── health.py
│   │   ├── verification.py
│   │   └── reports.py
│   ├── services/
│   │   ├── pdf_service.py
│   │   ├── claims_service.py
│   │   ├── comparison_service.py
│   │   ├── report_service.py
│   │   └── research_service.py
│   ├── providers/
│   │   └── anakin_client.py
│   └── schemas/
│       ├── supplier.py
│       ├── evidence.py
│       ├── finding.py
│       └── verification.py
└── tests/
```

### 3.4 Anakin Adapter

Keep Anakin behind a provider interface.

Recommended interface:

```python
class ResearchProvider(Protocol):
    async def search(self, query: str) -> list[Evidence]: ...
```

This prevents the rest of the application from depending directly on provider-specific response shapes.

### 3.5 PDF Service

Use PyMuPDF first.

Pipeline:

```text
PDF
 ↓
Text extraction
 ↓
Text cleanup
 ↓
Structured claim extraction
 ↓
Normalized Claim objects
```

OCR is out of the first milestone unless a demo document requires it.

## 4. Domain Model

### Supplier

```text
id
name
website
location
email
phone
product
created_at
```

### VerificationRequest

```text
id
supplier_id
purchase_amount
document_id
status
created_at
```

### Claim

```text
id
verification_id
field
value
source_type
source_locator
confidence
```

### Evidence

```text
id
verification_id
field
value
source_url
source_title
excerpt
retrieved_at
```

### Finding

```text
id
verification_id
field
status
document_value
evidence_value
explanation
evidence_ids
```

## 5. Finding State Machine

```text
                 ┌──────────────┐
                 │   NOT_FOUND  │
                 └──────────────┘
                        ▲
                        |
Claim ──> Comparison ───┼──> NEEDS_VERIFICATION
                        |
                        ├──> CONSISTENT
                        |
                        └──> MISMATCH
```

`NOT_FOUND` means no useful evidence was located. It does not mean the claim is false.

`NEEDS_VERIFICATION` means evidence exists but is insufficient to confidently reconcile the claim.

## 6. Agent Boundary

The LLM/agent may:
- Extract candidate claims
- Generate research queries
- Summarize evidence
- Draft explanations
- Draft verification messages

Deterministic code should own:
- Input validation
- Normalization rules
- Status enum validation
- Source URL validation
- Finding schema validation
- Final persistence
- Security/secret handling

## 7. Evidence Contract

Every evidence item should contain:

```json
{
  "source_url": "https://example.com",
  "source_title": "Example Company",
  "field": "address",
  "value": "Bengaluru",
  "excerpt": "...",
  "retrieved_at": "2026-09-20T10:00:00Z"
}
```

Do not store an LLM claim without knowing whether it came from:
- user input
- uploaded document
- public web source
- generated inference

## 8. API Surface

Initial backend endpoints:

```text
GET  /health
POST /api/v1/verifications
POST /api/v1/verifications/{id}/document
POST /api/v1/verifications/{id}/research
GET  /api/v1/verifications/{id}
GET  /api/v1/verifications/{id}/report
POST /api/v1/verifications/{id}/verification-request
```

The exact endpoint set may be simplified if DronaHQ handles orchestration directly.

## 9. Error Handling

Provider failures must be isolated.

Example:

```text
Anakin unavailable
      ↓
Research status = unavailable
      ↓
No fabricated evidence
      ↓
Report shows source unavailable
```

## 10. Deployment Strategy

Development:
- Local FastAPI
- Local frontend/app configuration
- `.env` secrets

Hackathon:
- Deploy to supported Nasiko infrastructure
- Configure production secrets securely
- Run an end-to-end smoke test

## 11. Architecture Rules

1. Provider APIs are adapters.
2. Domain models are provider-independent.
3. No LLM-generated values bypass validation.
4. No source without provenance may be shown as external evidence.
5. UI must consume stable response schemas.
6. The core vertical slice must work without optional features.
