# Simple unit tests for the new services
from backend.services.compiler.pipeline import compile_hus
from backend.services.ledger import Ledger, read_escrow, write_escrow
from backend.services.logistics import calculate_shipping
import os
import tempfile


def test_compiler_basic():
    src = '''
    contract order_contract {
      version: 1
      name: "OrderContract"
      owner: ${env.OWNER}
    }
    '''
    out = compile_hus(src, context={"env.OWNER": "Hussam"})
    assert isinstance(out, list) and len(out) == 1
    assert out[0]["body"]["name"] == "OrderContract"
    assert "stamps" in out[0]["body"]


def test_ledger_and_escrow(tmp_path):
    # Use temp tenant to avoid collisions
    ledger = Ledger(tenant_id=9999)
    tx_id = ledger.create_transaction(100.0, "USD", description="test")
    assert isinstance(tx_id, int)
    rows = ledger.list_transactions()
    assert any(r["description"] == "test" for r in rows)

    # escrow read/write
    escrow = read_escrow()
    escrow_key = "test-session-1"
    escrow[escrow_key] = {"status": "pending"}
    write_escrow(escrow)
    escrow2 = read_escrow()
    assert escrow_key in escrow2


def test_logistics():
    r = calculate_shipping("Sana'a", "Taiz", weight_kg=2.5, service="express")
    assert "estimated_cost_usd" in r
    assert r["distance_km"] > 0

if __name__ == '__main__':
    test_compiler_basic()
    test_ledger_and_escrow(None)
    test_logistics()
    print("Local tests passed")
