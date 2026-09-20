# EvidenceBridge

**Verify before you pay.**

EvidenceBridge is an AI-powered supplier verification agent for businesses evaluating a new supplier before making a payment.

## Architecture & Documentation

Please refer to the `docs/` directory for the comprehensive documentation:
- [PRD](docs/prd.md)
- [Architecture](docs/architecture.md)
- [Design Guidelines](docs/design.md)
- [Engineering Rules](docs/rules.md)
- [Task Plan](docs/tasks.md)
- [Project Memory](docs/memory.md)

## Repository Structure
- `backend/` - FastAPI backend application and services
- `docs/` - Project documentation (Source of Truth)
- `tests/` - Tests for the backend logic (Alternatively under backend/tests/)

The UI surface is built on **DronaHQ**.

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials.
2. Setup a python virtual environment (Python 3.11+).
3. Install dependencies from `backend/requirements.txt` (once generated).
4. Run the FastAPI dev server.
