from fastapi import APIRouter, HTTPException
from uuid import uuid4
from typing import Dict
from ..services.ledger import read_escrow, write_escrow, Ledger
from ..schemas.payments import CreatePaymentRequest, CreatePaymentResponse, VerifyPaymentRequest, VerifyPaymentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

# In-memory mapping of provider simulation handlers

class ProviderBase:
    name: str
    def create_session(self, payload: CreatePaymentRequest) -> Dict:
        raise NotImplementedError
    def verify(self, session_id: str) -> Dict:
        raise NotImplementedError

class AlKuraimiProvider(ProviderBase):
    name = "al_kuraimi"
    def create_session(self, payload: CreatePaymentRequest) -> Dict:
        # Simulate returning a QR code URL or payment reference
        ref = f"MFLOOS-{uuid4().hex[:12]}"
        return {"reference": ref, "qr_url": f"https://pay.alkuraimi.example/qr/{ref}"}
    def verify(self, session_id: str) -> Dict:
        # deterministic success for simulation
        return {"status": "paid", "provider_reference": session_id}

class AlNajmProvider(ProviderBase):
    name = "al_najm"
    def create_session(self, payload: CreatePaymentRequest) -> Dict:
        token = f"NAJM-{uuid4().hex[:10]}"
        return {"checkout_url": f"https://alnajm.example/checkout/{token}", "token": token}
    def verify(self, session_id: str) -> Dict:
        return {"status": "paid", "provider_reference": session_id}

class PocketProvider(ProviderBase):
    name = "pocket"
    def create_session(self, payload: CreatePaymentRequest) -> Dict:
        token = f"POCKET-{uuid4().hex[:10]}"
        return {"deep_link": f"pocket://pay/{token}", "token": token}
    def verify(self, session_id: str) -> Dict:
        return {"status": "paid", "provider_reference": session_id}

class CODProvider(ProviderBase):
    name = "cod"
    def create_session(self, payload: CreatePaymentRequest) -> Dict:
        # COD creates an escrow entry awaiting delivery confirmation
        return {"escrow_note": "Cash on Delivery - escrow created"}
    def verify(self, session_id: str) -> Dict:
        # COD remains pending until delivery confirmation in real systems
        return {"status": "pending", "provider_reference": session_id}

PROVIDERS = {
    "al_kuraimi": AlKuraimiProvider(),
    "al_najm": AlNajmProvider(),
    "pocket": PocketProvider(),
    "cod": CODProvider(),
}


def _load_escrow() -> Dict:
    return read_escrow()

@router.post("/create_payment_session", response_model=CreatePaymentResponse)
async def create_payment_session(req: CreatePaymentRequest):
    if req.method not in PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported payment method")
    provider = PROVIDERS[req.method]
    session_id = uuid4().hex
    # Persist an escrow entry
    escrow = _load_escrow()
    escrow[session_id] = {
        "tenant_id": req.tenant_id,
        "amount": req.amount,
        "currency": req.currency,
        "method": req.method,
        "description": req.description,
        "status": "pending",
        "created_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
    # provider-specific payload
    provider_payload = provider.create_session(req)
    escrow[session_id]["provider_payload"] = provider_payload
    write_escrow(escrow)

    # Return response shaped for frontend
    return CreatePaymentResponse(
        session_id=session_id,
        provider=provider.name,
        next_action="redirect" if "checkout_url" in provider_payload else "present_qr_or_link",
        metadata=provider_payload,
    )

@router.post("/verify_payment", response_model=VerifyPaymentResponse)
async def verify_payment(req: VerifyPaymentRequest):
    escrow = _load_escrow()
    if req.session_id not in escrow:
        raise HTTPException(status_code=404, detail="Session not found")
    entry = escrow[req.session_id]
    method = entry.get("method")
    provider = PROVIDERS.get(method)
    if not provider:
        raise HTTPException(status_code=400, detail="Unknown provider")
    result = provider.verify(req.session_id)
    status = result.get("status", "pending")
    # Update escrow and optional ledger record for paid
    entry["status"] = status
    entry.setdefault("verified_at", __import__("datetime").datetime.utcnow().isoformat() + "Z")
    write_escrow(escrow)

    if status == "paid":
        # Record to ledger
        ledger = Ledger(entry["tenant_id"])
        ledger.create_transaction(entry["amount"], entry["currency"], description=f"payment {req.session_id}")

    return VerifyPaymentResponse(session_id=req.session_id, status=status, details=result)
