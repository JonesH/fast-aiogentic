"""FastAPI application."""
from fastapi import FastAPI
from pydantic import BaseModel


class StatusResponse(BaseModel):
    """Status response with frozen immutability."""

    status: str
    service: str

    model_config = {"frozen": True}


class HealthResponse(BaseModel):
    """Health check response with frozen immutability."""

    status: str

    model_config = {"frozen": True}


app = FastAPI(title="fast-aiogentic", version="0.1.0")


@app.get("/")
async def root() -> StatusResponse:
    """Root endpoint."""
    return StatusResponse(status="ok", service="fast-aiogentic")


@app.get("/health")
async def health() -> HealthResponse:
    """Health check."""
    return HealthResponse(status="healthy")
