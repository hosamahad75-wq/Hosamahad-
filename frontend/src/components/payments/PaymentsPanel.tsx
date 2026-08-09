import React, { useState } from "react";
import PaymentSelector from "@/components/payments/PaymentSelector";
import PaymentCheckoutModal from "@/components/payments/PaymentCheckoutModal";
import PaymentStatus from "@/components/payments/PaymentStatus";
import { CreatePaymentRequest, CreatePaymentResponse } from "@/types/payments";

export default function PaymentsPanel() {
  const [method, setMethod] = useState<"al_kuraimi" | "al_najm" | "pocket" | "cod" | null>(null);
  const [session, setSession] = useState<CreatePaymentResponse | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [amount, setAmount] = useState<number>(10.0);
  const [currency, setCurrency] = useState<"USD" | "SAR" | "YER_SANAA" | "YER_ADEN">("USD");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createSession = async () => {
    if (!method) return;
    setLoading(true);
    setError(null);
    try {
      const payload: CreatePaymentRequest = {
        tenant_id: 1,
        amount: amount,
        currency,
        method,
        description: "Checkout",
      };
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/payments/create_payment_session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Create session failed: ${res.status}`);
      const data: CreatePaymentResponse = await res.json();
      setSession(data);
      setSessionId(data.session_id);
    } catch (err: any) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Checkout</h2>
          <div className="text-sm text-neutral-400">Select a payment method and confirm</div>
        </div>
        <div className="flex gap-2 items-center">
          <input type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} className="w-28 p-2 rounded-md bg-black/30" />
          <select value={currency} onChange={(e) => setCurrency(e.target.value as any)} className="p-2 rounded-md bg-black/30">
            <option value="USD">USD</option>
            <option value="SAR">SAR</option>
            <option value="YER_SANAA">YER Sana'a</option>
            <option value="YER_ADEN">YER Aden</option>
          </select>
        </div>
      </div>

      <PaymentSelector selected={method ?? undefined} onSelect={(m) => setMethod(m)} />

      {error && <div className="text-rose-400">Error: {error}</div>}

      <div className="flex justify-end">
        <button
          disabled={!method || loading}
          onClick={createSession}
          className="px-4 py-2 rounded-md bg-cyan-500 text-black font-semibold disabled:opacity-50"
        >
          {loading ? "Processing..." : "Pay Now"}
        </button>
      </div>

      <PaymentStatus sessionId={sessionId} onPaid={(details) => alert("Payment confirmed")}/>

      <PaymentCheckoutModal session={session} onClose={() => setSession(null)} />
    </div>
  );
}
