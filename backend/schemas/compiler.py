from pydantic import BaseModel
from typing import Any, Dict

class ContractModel(BaseModel):
    __contract: str
    __type: str
    __generated_at: str
    body: Dict[str, Any]
