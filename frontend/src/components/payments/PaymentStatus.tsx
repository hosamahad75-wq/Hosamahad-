import React, { useEffect, useRef, useState } from "react";
import { VerifyPaymentResponse } from "@/types/payments";

interface Props {
  sessionId: string | null;
  onPaid?: (details: any) => void;
}

export default function PaymentStatus({ sessionId, onPaid }: Props) {
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const statusRef = useRef<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    let stopped = false;
    setLoading(true);
    setError(null);
    setStatus("pending");
    statusRef.current = "pending";

    const check = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/payments/verify_payment`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: VerifyPaymentResponse = await res.json();
        if (stopped) return;
        setStatus(data.status);
        statusRef.current = data.status;
        setLoading(false);
        if (data.status === "paid") {
          onPaid?.(data.details);
        }
      } catch (err: any) {
        setError(err.message || String(err));
        setLoading(false);
      }
    };

    // Polling strategy: try immediately, then every 3s up to 1 minute
    let attempts = 0;
    check();
    const iv = setInterval(() => {
      attempts += 1;
      if (attempts >= 20 || statusRef.current === "paid") {
        clearInterval(iv);
        return;
      }
      check();
    }, 3000);

    return () => {
      stopped = true;
      clearInterval(iv);
    };
  }, [sessionId]);

  if (!sessionId) return null;

  return (
    <div className="mt-3 p-3 rounded-md bg-gradient-to-br from-black/50 to-white/2 border border-white/5">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-neutral-300">Payment status</div>
          <div className="font-semibold text-lg">{status ?? "unknown"}</div>
        </div>
        <div>
          {loading && <div className="text-sm text-neutral-400">Checking...</div>}
          {error && <div className="text-sm text-rose-400">Error: {error}</div>}
        </div>
      </div>
    </div>
  );
}
