from pydantic import BaseModel, Field
from typing import Literal, Optional

class CreatePaymentRequest(BaseModel):
    tenant_id: int
    amount: float
    currency: Literal["USD", "SAR", "YER_SANAA", "YER_ADEN"]
    method: Literal["al_kuraimi", "al_najm", "pocket", "cod"]
    description: Optional[str] = None

class CreatePaymentResponse(BaseModel):
    session_id: str
    provider: str
    next_action: str
    metadata: dict = Field(default_factory=dict)

class VerifyPaymentRequest(BaseModel):
    session_id: str

class VerifyPaymentResponse(BaseModel):
    session_id: str
    status: Literal["pending", "paid", "failed", "cancelled"]
    details: dict = Field(default_factory=dict)
