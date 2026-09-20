# EvidenceBridge — Engineering Rules

This document is the operating contract for developers and AI coding agents, including Antigravity.

## 1. Source of Truth

Priority order:

1. `docs/prd.md`
2. `docs/architecture.md`
3. `docs/design.md`
4. `docs/tasks.md`
5. `docs/memory.md`
6. Existing code/tests

When implementation conflicts with the PRD or architecture, stop and resolve the conflict rather than silently changing product behavior.

## 2. AI Coding Agent Rules

Before changing code:
- Read the relevant docs.
- Inspect the existing implementation.
- Reuse existing utilities/components where practical.
- Make the smallest coherent change.
- Update tests for behavior changes.
- Update `docs/memory.md` when a major implementation decision changes.

Never:
- Rewrite unrelated files.
- Introduce a new framework without a clear need.
- Duplicate provider clients.
- Hard-code secrets.
- Add fake production integrations just to make a demo appear complete.
- Claim an external API works without testing the real integration or clearly marking it as mocked.

## 3. Python Rules

- Python 3.11+.
- Type hints for public functions.
- Pydantic models for API boundaries.
- Async I/O for network-bound provider calls.
- Keep business logic out of route handlers.
- Use structured logging.
- Catch provider errors at integration boundaries.
- Raise domain-specific errors where appropriate.

## 4. FastAPI Rules

- Version application APIs under `/api/v1`.
- Keep routes thin.
- Validate request/response schemas.
- Never return raw provider responses directly to the frontend unless explicitly intended.
- Add health checks.

## 5. Provider Integration Rules

Every external provider must have an adapter.

Do not do this throughout the codebase:

```python
requests.post("https://provider.example/api", ...)
```

Instead:

```text
services
   ↓
provider interface
   ↓
provider adapter
```

Provider-specific JSON stays inside the adapter.

## 6. Evidence Rules

Evidence must have provenance.

Required fields:
- source URL
- source title when available
- field being supported
- extracted value
- excerpt/snippet when available
- retrieval timestamp

Never convert:

`not_found`

into:

`false`.

Never convert:

`insufficient evidence`

into:

`fraud`.

## 7. AI Output Rules

Prefer structured JSON outputs.

Every structured AI response must be validated before entering domain logic.

The model may propose:
- claims
- queries
- explanations
- recommended questions

The model may not bypass:
- schema validation
- source validation
- status enums
- authorization checks
- application rules

## 8. Security Rules

- Secrets go in environment variables/platform secrets.
- `.env` must be gitignored.
- `.env.example` must contain placeholder values only.
- Never log API keys.
- Never expose secret provider keys to browser code.
- Validate uploaded file types and size.

## 9. Frontend/UI Rules

- Keep the interface calm and professional.
- Avoid excessive gradients, glassmorphism, glowing AI effects, or generic neon AI styling.
- Use clear hierarchy and whitespace.
- Evidence should be visually distinguishable from AI-generated explanation.
- Status colors must communicate state consistently.
- Loading/progress states must be explicit.
- Error states must be actionable.

## 10. Testing Rules

At minimum:
- unit tests for normalization
- unit tests for comparison logic
- API schema tests
- provider adapter tests with mocked responses
- one end-to-end smoke test

Critical comparison logic should be deterministic and should not require an LLM in unit tests.

## 11. Git Rules

Commit messages should be small and descriptive:

```text
feat: add supplier intake schema
feat: add pdf claim extraction
feat: add anakin research adapter
feat: add evidence comparison
feat: add verification report
fix: handle provider timeout
```

Do not commit generated secrets, temporary documents, screenshots containing private data, or large build artifacts.

## 12. Scope Rules

During the hackathon:

> Working P0 > polished P1 > ambitious backlog.

Do not add authentication, payments, mobile, complex analytics, or large integrations until the P0 vertical slice is working.

## 13. Definition of Quality

A feature is not done when it renders.

A feature is done when:
- the happy path works
- invalid input is handled
- failure states are visible
- the response schema is stable
- tests cover the important behavior
- docs/memory are updated when appropriate

## 14. Antigravity Prompting Standard

When asking Antigravity to code, each prompt should include:

1. Objective
2. Relevant files
3. Constraints
4. Expected behavior
5. Tests required
6. Definition of done

Example:

```text
Objective:
Implement supplier claim normalization.

Read first:
- docs/prd.md
- docs/architecture.md
- docs/rules.md

Constraints:
- Do not change API contracts outside this feature.
- Use Pydantic.
- No LLM call in the normalization layer.

Expected:
- Normalize company name, URL, phone and address.
- Return deterministic normalized fields.

Tests:
- Add unit tests for whitespace, URL normalization and phone formatting.

Done when:
- Tests pass.
- Type checks pass.
- No unrelated files changed.
```
