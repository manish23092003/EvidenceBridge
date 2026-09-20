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

**Next implementation task:** T1.1 Domain Schemas
