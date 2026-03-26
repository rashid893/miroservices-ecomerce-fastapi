"""
Shared Pydantic schemas used conceptually across services.
Each service defines its own schemas — these are for documentation/reference only.
Do NOT import these directly into services to avoid coupling.
"""
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    service: str

class ErrorResponse(BaseModel):
    detail: str
