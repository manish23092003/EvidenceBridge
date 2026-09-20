# EvidenceBridge — Project Memory

This file is the living context anchor for future coding sessions and AI coding agents.

## 1. Current Identity

**Project:** EvidenceBridge
**Tagline:** Verify before you pay.
**Stage:** Hackathon MVP
**Primary event:** Nasiko Build-A-Thon

## 2. Current Product Thesis

Businesses need a fast way to identify supplier claims that are supported, conflicting, or still unverified before making a payment.

EvidenceBridge connects supplier-submitted information to public evidence and turns the comparison into actionable verification steps.

## 3. Non-Negotiable Product Boundary

EvidenceBridge is decision support.

It must not claim:
- a supplier is definitely fraudulent
- a supplier is definitely safe
- a public-web absence proves a company is fake
- an AI-generated conclusion is authoritative without evidence

## 4. Core Vertical Slice

```text
Supplier input
    ↓
Quotation PDF
    ↓
Claim extraction
    ↓
Anakin research
    ↓
Evidence normalization
    ↓
Claim/evidence comparison
    ↓
Finding
    ↓
Verification report
    ↓
Verification request
```

## 5. Technology Decisions

### Confirmed direction
- DronaHQ for app/agent workflow
- Anakin for public web research
- FastAPI for custom services
- PyMuPDF for PDF extraction
- PostgreSQL only if persistence is necessary for MVP
- Nasiko for deployment/control-plane integration
- Antigravity for AI-assisted development

### Principle
Keep provider-specific logic behind adapters.

## 6. Current Architecture Rule

Deterministic code owns:
- normalization
- comparison
- schema validation
- status classification
- security
- persistence

AI owns:
- extraction proposal
- query planning
- evidence summarization
- message drafting

## 7. Current UI Direction

Professional B2B procurement tool.

Avoid generic AI aesthetics.

Primary flow:

`Input → Progress → Findings → Evidence → Action`

## 8. Demo Data

Supplier:
`ABC Industrial Solutions`

Purchase:
`₹1,80,000`

Product:
`Industrial CNC component`

The final demo fixture should be synthetic and clearly controlled. Any apparent mismatch must be intentionally seeded and documented so the demo is reproducible.

## 9. Current Progress

- [x] Product concept selected
- [x] Initial PRD drafted
- [x] Architecture drafted
- [x] Engineering rules drafted
- [x] UI/design direction drafted
- [x] Task plan drafted
- [x] Project memory initialized
- [ ] Repository implementation
- [ ] DronaHQ setup
- [ ] Anakin setup
- [ ] FastAPI implementation
- [ ] Nasiko deployment
- [ ] Demo recording

## 10. Decision Log

### 2026-09-20 — Name change
Changed working name from `TrustFlow` to `EvidenceBridge` before coding.
Reason: clearer expression of evidence-driven verification and lower collision risk than several obvious supplier-risk names already in use.

### 2026-09-20 — Scope decision
Chose one strong vertical slice rather than a broad procurement platform.
Reason: one-day hackathon constraint.

### 2026-09-20 — Evidence policy
Chose evidence + verification-gap language instead of fraud/safe labels.
Reason: public web information is incomplete and automated findings should remain auditable and appropriately uncertain.

## 11. Open Decisions

- Exact DronaHQ-to-FastAPI boundary
- Exact Anakin API mode for the demo
- Whether PostgreSQL is needed for the final demo
- Exact Nasiko deployment path
- Final typography/accent color

## 12. Session Handoff Template

At the end of each significant coding session, update:

### Completed
- ...

### Current task
- ...

### Changed files
- ...

### Decisions
- ...

### Known issues
- ...

### Next task
- ...

### Last verified command
```text
...
```

## 13. Current Project State

- Development baseline is complete.
- Python dependency management uses uv.
- Backend uses FastAPI.
- Ruff is used for linting/formatting.
- Pytest is the test framework.
- MyPy is enabled.
- Health endpoint is implemented at `backend/app/api/health.py`.
- Current branch is `main`.
- GitHub origin is configured but the repository has not been pushed yet.
- **T1.1 Domain Schemas Complete:**
  - Implemented 5 core models: `Supplier`, `VerificationRequest`, `Claim`, `Evidence`, `Finding`.
  - Used `pydantic[email]` (which brought in `email-validator`) to support clean `EmailStr` typing on the Supplier model.
  - Ensured models remain pure data representations with no API, DB, or external provider logic.
  - Used UTC timezone-aware defaults for all `created_at` fields.
  - Exposed models via `app.schemas`.
  - Fully tested all requirements and passing Ruff/MyPy strict type checks.


- **T1.2 Intake API Complete:**
  - **Endpoint:** `POST /api/v1/verification-requests` returning HTTP 201.
  - **Schema:** Defined distinct API-facing schemas `CreateVerificationRequest` and `CreateVerificationResponse` in `schemas/intake.py` to decouple from domain models.
  - **Service:** Logic offloaded to `VerificationService` in `services/verification_service.py` to act as a pure functional layer instantiating domain objects.
  - **Note:** Persistence is intentionally NOT implemented yet; the API simply returns the constructed data models.
- **T1.3 Basic UI Pending Manual Setup:**
  - **Status:** DronaHQ UI specification is prepared. T1.3 is NOT complete.
  - **Action Required:** Actual DronaHQ app creation and API connection must be manually verified.
  - **Next Backend Step:** Next backend implementation task can proceed independently with T2.1 PDF service.


- **T2.3 Claim Extraction Complete:**
  - **Tooling:** Implemented `google-genai` SDK using Gemini 2.5 Flash as the default.
  - **Architecture:** Created an `LLMProvider` protocol to ensure Gemini doesn't leak into the domain layer.
  - **Data Handling:** Designed a strict `ExtractedClaim` Pydantic model. LLM yields structured JSON automatically mapped to domain `Claim` models.
  - **Constraints:** LLM is restricted from generating IDs, timestamps, or guessing absent data. Extraction logic handles these safely.

- **T2.2 Document Intake Complete:**
  - **Endpoint:** `POST /api/v1/documents/extract` explicitly configured for `multipart/form-data` using FastAPI's `UploadFile`.
  - **Boundary:** Remains a stateless HTTP adapter. It reads bytes directly into memory and passes them to `PdfService`.
  - **Validation:** Relies securely on backend parsing rather than trusting user-provided MIME types or extensions.
  - **Error Mapping:** Cleanly translates internal `PdfServiceError` hierarchy to appropriate HTTP codes (400, 413, 422).
  - **Dependencies:** Added `python-multipart` to support FastAPI's native form parsing.

- **T2.1 PDF Service Complete:**
  - **Tooling:** PyMuPDF (`fitz`) handles direct byte extraction securely in-memory.
  - **Configuration:** Limits exposed via `.env` (default 10 MB size, 20 pages max).
  - **Constraints:** OCR is intentionally excluded (raises `PdfNoTextError` when only images exist). File system storage is skipped.
  - **Exceptions:** Handled internally and re-raised as domain-specific exceptions (`PdfTooLargeError`, `InvalidPdfError`, etc.).

- **T3.1 Anakin Research Provider Adapter Complete:**
  - **Tooling:** Implemented via a minimal REST adapter (`httpx`) connecting to the Anakin synchronous search endpoint, circumventing undocumented alpha SDK issues while retaining full control over timeout semantics.
  - **Abstraction:** Introduced `WebResearchProvider` protocol and `SearchResult` schema, keeping Anakin's specific JSON structure isolated from the domain schemas.
  - **Constraints:** Returns a provider-neutral Pydantic model (`SearchResult`). No business evaluations, trust scores, or final `Evidence` mapping occurs here; it strictly executes search operations.
  - **Tests:** Fully mocked using `httpx` monkeypatching without requiring an actual API key for CI pipelines. Translates `httpx` timeout/status errors into our structured `WebResearchError` hierarchy safely.

- **T3.2 Research Planner Complete:**
  - **Tooling:** Implemented `ResearchPlannerService` purely in domain logic. No HTTP or Database interactions.
  - **Architecture:** Introduced `ResearchQuery` schema with deterministic grouping/deduplication based on exact query strings. Traceability maintained via accumulating `claim_ids`.
  - **Constraints:** Max queries capped securely by `RESEARCH_MAX_QUERIES=5`. Enforced custom Enum priority sorting (`ResearchPurpose`). Web logic never invents names; it falls back safely.
  - **Tests:** Full mock coverage verifying correct query formations, limit capping, deterministic output, and preservation of procurement privacy constraints (ignores purchase_amount/currency etc.).

- **T3.3 Research Orchestration Complete:**
  - **Tooling:** Implemented `ResearchService` to orchestrate `ResearchPlannerService` and `WebResearchProvider`.
  - **API:** Exposed `POST /api/v1/research` as an Artisan-ready REST endpoint.
  - **Constraints:** Strict error handling intercepts HTTP timeouts and rate limits, replacing them with safe messages. Failed provider queries result in `FAILED` statuses without halting the entire pipeline.
  - **Traceability:** Results correctly maintain original `claim_ids`, preparing for evidence mapping.

**Next implementation task:** T4.3 Failure handling or T5 Verification Reporting (whichever task follows T4.2)

- **T4.2 Evidence Comparison Engine Complete:**
  - **Schema:** Defined `ComparisonEvaluation` matching `FindingStatus` enum (CONSISTENT, MISMATCH, NEEDS_VERIFICATION, NOT_FOUND).
  - **Tooling:** Implemented `EvidenceComparisonService` which maps `Evidence` to `Claim`, filters out irrelevant evidence, and instructs the `LLMProvider` using a strict system prompt.
  - **Constraints:** Guarantees LLM never invents evidence. Sanitizes returned `evidence_ids` against actual supplied IDs. Handles LLM errors gracefully by downgrading failure directly to `NEEDS_VERIFICATION` without bringing the system down.
  - **Tests:** Confirmed correct `NOT_FOUND` generation internally without LLM calls, and confirmed safe degradation of external HTTP errors.

- **T4.1 Evidence Normalization Complete:**
  - **Schema:** Modified `Evidence` to hold `claim_ids: list[str]`. This explicitly establishes traceability mapping back to the extracted claims via `EvidenceService`.
  - **Tooling:** Implemented `EvidenceService.normalize_research_results()` to perform intelligent deduplication of query results.
  - **Constraints:** Extracts only meaningful evidence logic (`content` first, then `snippet`), throwing away blank searches or failed providers cleanly. It intentionally *defers* any determination of whether the evidence proves or disputes the claim, pushing business reasoning strictly to T4.2.
