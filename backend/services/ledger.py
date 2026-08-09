from __future__ import annotations
import sqlite3
import threading
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

class Ledger:
    """Simple file-backed multi-tenant ledger with per-tenant sqlite DB files.

    This implementation keeps tenant isolation by storing each tenant's transactions in a separate sqlite file
    (backend/data/tenant_{tenant_id}.db). It includes multi-currency conversion utilities for USD, SAR, YER_SANAA, YER_ADEN.
    """
    RATES = {
        # rates relative to USD
        "USD": 1.0,
        "SAR": 0.2666,     # 1 SAR ~= 0.2666 USD (example)
        "YER_SANAA": 0.0019, # example rates
        "YER_ADEN": 0.0020,
    }

    _locks = {}

    def __init__(self, tenant_id: int):
        self.tenant_id = int(tenant_id)
        self.db_path = os.path.join(DATA_DIR, f"tenant_{self.tenant_id}.db")
        self._ensure_db()

    def _get_lock(self):
        if self.tenant_id not in self._locks:
            self._locks[self.tenant_id] = threading.Lock()
        return self._locks[self.tenant_id]

    def _ensure_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                converted_usd REAL NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL
            )
            """)
            conn.commit()
        finally:
            conn.close()

    def convert_to_usd(self, amount: float, currency: str) -> float:
        currency = currency.upper()
        if currency not in self.RATES:
            raise ValueError(f"Unsupported currency: {currency}")
        rate = float(self.RATES[currency])
        usd = float(Decimal(amount * rate).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP))
        return usd

    def create_transaction(self, amount: float, currency: str, description: Optional[str] = "") -> int:
        with self._get_lock():
            converted = self.convert_to_usd(amount, currency)
            conn = sqlite3.connect(self.db_path)
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO transactions (amount, currency, converted_usd, description, created_at) VALUES (?, ?, ?, ?, ?)",
                    (amount, currency.upper(), converted, description, datetime.utcnow().isoformat() + "Z"),
                )
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()

    def list_transactions(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, amount, currency, converted_usd, description, created_at FROM transactions ORDER BY id DESC")
            rows = cur.fetchall()
            return [dict(id=r[0], amount=r[1], currency=r[2], converted_usd=r[3], description=r[4], created_at=r[5]) for r in rows]
        finally:
            conn.close()

# Lightweight escrow store for payments (JSON file)
ESCROW_FILE = os.path.join(DATA_DIR, "escrow.json")

def read_escrow():
    if not os.path.exists(ESCROW_FILE):
        return {}
    with open(ESCROW_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def write_escrow(data):
    with open(ESCROW_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
