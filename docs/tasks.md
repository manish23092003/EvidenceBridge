# EvidenceBridge — Task Plan

**Version:** 0.1.0
**Execution style:** vertical-slice-first

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Complete
- `[!]` Blocked

## Milestone 0 — Repository Foundation

### T0.1 Create project structure
- [ ] Create `/docs`
- [ ] Create source directories
- [ ] Create `.gitignore`
- [ ] Create `.env.example`
- [ ] Create `README.md`

### T0.2 Development baseline
- [x] Choose Python environment strategy
- [x] Add dependency management
- [x] Add linting/type-checking configuration
- [x] Add test framework
- [x] Add basic health endpoint

**Verification Results:**
- uv project initialized
- FastAPI baseline working
- pytest passing
- Ruff linting passing
- Ruff formatting passing
- MyPy passing
- `/health` endpoint returning HTTP 200
- No unresolved implementation errors

### T0.3 Agent instructions
- [ ] Configure Antigravity workflow using `docs/rules.md`
- [ ] Ensure generated changes respect the source-of-truth hierarchy

## Milestone 1 — Supplier Intake

### T1.1 Domain schemas
- [x] Supplier model
- [x] VerificationRequest model
- [x] Claim model
- [x] Evidence model
- [x] Finding model
### T1.2 Intake API
- [x] Create verification request endpoint
- [x] Validate supplier fields
- [x] Validate amount
- [x] Add API tests

### [~] T1.3 Basic UI — DronaHQ implementation pending manual setup
- [~] Supplier form
- [~] Document upload
- [~] Validation messages
- [~] Start verification CTA

> DronaHQ UI specification prepared, but the cloud-hosted application has not yet been manually created and verified. Backend/API integration is ready.

## Milestone 2 — Document Processing

### T2.1 PDF service
- [x] Install/configure PyMuPDF
- [x] Extract text
- [x] Handle empty/scanned PDFs gracefully
- [x] Add file size/type validation
### T2.2 Document Intake
- [x] Create document upload endpoint
- [x] Validate PDF contents
- [x] Integrate PDF service
- [x] Map exceptions to HTTP errors

### T2.3 Claim extraction
- [x] Define extraction prompt/schema
- [x] Extract supplier claims
- [x] Normalize fields
- [x] Validate structured response

### T2.4 Tests
- [ ] Unit test text extraction
- [ ] Unit test claim normalization
- [ ] Test malformed extraction response

## Milestone 3 — Web Research

### T3.1 Provider adapter
- [x] Create research provider interface
- [x] Create Anakin adapter
- [x] Configure API credentials securely
- [x] Normalize Anakin responses into Evidence objects

### T3.2 Research planner
- [x] Generate focused supplier queries
- [x] Control query volume
- [x] Map claims to queries
- [ ] Store retrieval timestamps

### T3.3 Research Orchestration
- [x] Integrate Research Planner and Web Provider
- [x] Process multiple queries securely
- [x] Isolate Provider Failures gracefully

## Milestone 4 — Evidence Comparison

### T4.1 Evidence normalization
- [x] Create Evidence domain service
- [x] Trace research results to claims
- [x] Standardize evidence objects

### T4.2 Comparison engine
- [x] Compare names
- [x] Compare address/location
- [x] Compare domain
- [x] Compare phone/email
- [x] Compare product/service

### T4.3 Finding classification
- [ ] CONSISTENT
- [ ] MISMATCH
- [ ] NEEDS_VERIFICATION
- [ ] NOT_FOUND

### T4.4 Deterministic tests
- [ ] Matching names
- [ ] Formatting-only differences
- [ ] Obvious mismatch
- [ ] Missing evidence
- [ ] Ambiguous evidence

## Milestone 5 — Report

### T5.1 Report schema
- [ ] Summary
- [ ] Finding list
- [ ] Evidence references
- [ ] Recommended actions

### T5.2 UI
- [ ] Summary cards
- [ ] Finding cards
- [ ] Evidence detail
- [ ] Source links

### T5.3 Action generator
- [ ] Checklist generation
- [ ] Verification message
- [ ] Copy-to-clipboard

## Milestone 6 — DronaHQ Integration

- [ ] Connect intake flow
- [ ] Connect verification workflow
- [ ] Connect agent/tool actions
- [ ] Display progress
- [ ] Display final report
- [ ] Handle integration errors

## Milestone 7 — Nasiko Integration

- [ ] Confirm runtime/deployment requirements
- [ ] Configure deployment
- [ ] Configure secrets
- [ ] Smoke-test deployed application

## Milestone 8 — Quality Gate

- [ ] Run unit tests
- [ ] Run API tests
- [ ] Run end-to-end demo test
- [ ] Check secret leakage
- [ ] Check broken links
- [ ] Check error states
- [ ] Check responsive layout

## Milestone 9 — Hackathon Submission

- [ ] Prepare GitHub PR
- [ ] Star/fork required repository if applicable
- [ ] Prepare 2-minute demo
- [ ] Prepare LinkedIn post
- [ ] Verify submission requirements
- [ ] Submit before deadline

## Critical Path

```text
T0 → T1 → T2 → T3 → T4 → T5
                      |
                      v
                 T6 + T7
                      |
                      v
                    T8
                      |
                      v
                    T9
```

## Cut Order Under Time Pressure

If time becomes limited, cut in this order:

1. Verification history
2. Export
3. Multiple documents
4. Advanced UI polish
5. Persistent database

Do NOT cut:
- evidence attribution
- comparison logic
- source URLs
- report
- end-to-end demo flow
