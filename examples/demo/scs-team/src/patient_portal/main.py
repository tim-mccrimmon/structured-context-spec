"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from patient_portal.routes import appointments, patients, messages

app = FastAPI(
    title="Patient Portal API",
    version="0.1.0",
    docs_url="/api/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://portal.acmehealth.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["appointments"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
