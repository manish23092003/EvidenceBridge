from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.api.report import router as report_router
from app.api.research import router as research_router
from app.api.verification_requests import router as verification_router

app = FastAPI(
    title="EvidenceBridge API",
    description="Backend services for EvidenceBridge supplier verification",
    version="0.1.0",
)

# Configure CORS for DronaHQ and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(verification_router)
app.include_router(documents_router)
app.include_router(research_router)
app.include_router(report_router)
