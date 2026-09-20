# EvidenceBridge — Product Requirements Document

**Version:** 0.1.0
**Status:** Hackathon MVP
**Event:** Nasiko Build-A-Thon
**Product tagline:** Verify before you pay.

## 1. Product Summary

EvidenceBridge is an AI-powered supplier verification agent for businesses evaluating a new supplier before making a payment.

The user provides supplier details and a quotation/invoice. EvidenceBridge extracts supplier claims, researches relevant public information, compares submitted claims against retrieved evidence, identifies mismatches and verification gaps, and generates a concise evidence-backed verification report with suggested next actions.

EvidenceBridge is decision support. It does not declare a supplier fraudulent, safe, legitimate, or illegitimate based only on automated research.

## 2. Problem

Supplier information is fragmented across quotations, invoices, websites, directories, public pages, and business communications. A small business may need to manually check whether names, addresses, contact details, products, payment terms, and public presence are consistent before paying a new supplier.

The problem we solve is:

> Help a business quickly identify supplier claims that are supported, conflicting, or still unverified before money moves.

## 3. Target Users

### Primary
- SME owner
- Procurement executive
- Operations/finance employee
- Startup founder

### Secondary
- Purchase managers
- Project managers buying from new vendors
- Freelancers or independent businesses making high-value purchases

## 4. Core User Journey

1. User opens EvidenceBridge.
2. User enters supplier details.
3. User uploads a quotation or invoice PDF.
4. EvidenceBridge extracts structured supplier claims.
5. The agent creates a focused research plan.
6. Anakin performs public web research.
7. Evidence is normalized and attached to source URLs.
8. Claims are compared with evidence.
9. Findings are classified as `CONSISTENT`, `MISMATCH`, `NOT_FOUND`, or `NEEDS_VERIFICATION`.
10. EvidenceBridge generates a verification report.
11. User generates a verification request/checklist.

## 5. MVP Scope

### P0 — Must Have

#### Supplier Intake
Fields:
- Supplier name
- Website
- Location
- Email
- Phone
- Product/service
- Purchase amount

#### Document Intake
- Upload quotation/invoice PDF.
- Extract text.
- Extract structured supplier claims.

#### Research
- Research supplier name, domain, address, product/service, and relevant public presence.
- Use Anakin for web research.
- Preserve source URL/title for every usable evidence item.

#### Comparison
Compare at minimum:
- Supplier/company name
- Address/location
- Website/domain
- Phone/email where present
- Product/service

#### Findings
Every finding must include:
- Field
- Submitted value
- Evidence value
- Status
- Explanation
- Source URL(s)

#### Report
Display:
- Supplier summary
- Purchase context
- Evidence coverage
- Findings
- Verification gaps
- Recommended next steps

#### Action Generator
Generate a professional verification request asking for missing documents/details.

### P1 — Only after P0 works
- Evidence source cards
- Verification history
- Multiple document comparison
- Exportable report
- Configurable verification checklist

### Out of Scope
- Payment execution
- Bank account verification
- Government-registry integrations without a confirmed API
- Fraud guarantee
- Legal/compliance certification
- Automatic approve/reject decisions
- Supplier marketplace
- Mobile app
- Enterprise RBAC

## 6. Product Principles

1. **Evidence before conclusion.** Findings must point to supporting evidence.
2. **No unsupported accusations.** Never label a supplier a scam based on weak signals.
3. **Show uncertainty.** Missing evidence is different from negative evidence.
4. **Human decision.** The user decides what to do next.
5. **Actionable output.** Every meaningful gap should result in a practical verification action.
6. **Demo reliability over feature count.** A complete vertical slice is more important than breadth.

## 7. Functional Requirements

### FR-01 Supplier Intake
The system shall accept supplier information through a form.

### FR-02 PDF Upload
The system shall accept a quotation/invoice PDF for processing.

### FR-03 Claim Extraction
The system shall transform document content into normalized structured claims.

### FR-04 Research
The system shall create focused research queries and collect public evidence.

### FR-05 Source Attribution
The system shall retain source metadata for evidence used in findings.

### FR-06 Comparison
The system shall compare selected supplier claims with retrieved evidence.

### FR-07 Finding Classification
Each supported comparison shall produce one of the defined statuses.

### FR-08 Verification Report
The system shall present findings in a readable report.

### FR-09 Action Generation
The system shall generate verification questions/documents based on gaps.

### FR-10 Graceful Failure
A failed web source or optional integration shall result in a visible `NOT_FOUND` / `UNAVAILABLE` state, not invented information.

## 8. Non-Functional Requirements

### Performance
The demo workflow should normally complete within a few minutes.

### Security
- Secrets must stay server-side.
- API keys must be stored in environment variables or platform secrets.
- Do not commit credentials.
- Do not expose provider keys to browser code.

### Explainability
Every important conclusion must be traceable to a source or explicitly marked as inference.

### Maintainability
Business logic should be modular and testable independently from UI and provider adapters.

## 9. Success Criteria

The hackathon MVP is successful when a judge can:

1. Enter a supplier.
2. Upload a quotation.
3. Start a verification run.
4. See the agent research.
5. See evidence with sources.
6. See a meaningful mismatch or verification gap.
7. Understand why that finding exists.
8. Generate a verification request.

## 10. Demo Scenario

Example supplier:

`ABC Industrial Solutions`

Example purchase:

`₹1,80,000 — Industrial CNC component`

The prepared demo document should contain realistic claims that can be checked against public web evidence. The final demo should demonstrate the full loop:

`Claim → Research → Evidence → Comparison → Finding → Action`

## 11. Technology Direction

- DronaHQ — application/workflow/agent surface
- Anakin — public web research
- Python + FastAPI — custom backend/services where needed
- PyMuPDF — PDF text extraction
- PostgreSQL — persistence if needed
- Nasiko — deployment/control-plane integration
- Antigravity — AI-assisted development, code generation, refactoring, debugging, testing

## 12. Definition of Done

- [ ] Repository structure created
- [ ] Environment configuration documented
- [ ] Supplier intake works
- [ ] PDF extraction works
- [ ] Structured claim extraction works
- [ ] Anakin research works
- [ ] Evidence objects store citations
- [ ] Comparison engine works
- [ ] Findings render correctly
- [ ] Verification report works
- [ ] Action generator works
- [ ] Error states work
- [ ] End-to-end test passes
- [ ] Demo deployment works
- [ ] GitHub PR ready
- [ ] Two-minute demo ready
