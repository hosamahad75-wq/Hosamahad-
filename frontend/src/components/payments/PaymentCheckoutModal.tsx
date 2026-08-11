import React from "react";
import { QRCodeCanvas } from "qrcode.react";
import { CreatePaymentResponse } from "@/types/payments";

interface Props {
  session: CreatePaymentResponse | null;
  onClose: () => void;
}

export default function PaymentCheckoutModal({ session, onClose }: Props) {
  if (!session) return null;

  const metadata = session.metadata || {};

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative max-w-lg w-full p-6 rounded-2xl bg-gradient-to-br from-black/60 to-white/3 border border-white/5">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">{session.provider} Payment</h3>
          <button className="text-sm text-neutral-400" onClick={onClose}>Close</button>
        </div>

        {/* Al-Kuraimi (QR) */}
        {metadata.reference && metadata.qr_url && (
          <div className="flex flex-col items-center gap-3">
            <QRCodeCanvas value={metadata.qr_url} size={180} fgColor="#00e5ff" bgColor="#0b1220" />
            <div className="text-sm text-neutral-300">Reference: <span className="font-mono ml-2">{metadata.reference}</span></div>
            <div className="flex gap-2 mt-2">
              <a href={metadata.qr_url} target="_blank" rel="noreferrer" className="px-4 py-2 rounded-md bg-cyan-600 text-black font-semibold">Open</a>
              <button
                onClick={() => navigator.clipboard.writeText(metadata.reference)}
                className="px-4 py-2 rounded-md border border-white/10 text-sm"
              >Copy Ref</button>
            </div>
          </div>
        )}

        {/* Al-Najm */}
        {metadata.checkout_url && (
          <div className="flex flex-col items-center gap-3">
            <p className="text-sm text-neutral-300">Proceed to Al-Najm to complete the payment.</p>
            <a href={metadata.checkout_url} target="_blank" rel="noreferrer" className="px-4 py-2 rounded-md bg-cyan-600 text-black font-semibold">Proceed to Al‑Najm Checkout</a>
          </div>
        )}

        {/* Pocket deep link */}
        {metadata.deep_link && (
          <div className="flex flex-col items-center gap-3">
            <p className="text-sm text-neutral-300">Open your Pocket app to complete the payment.</p>
            <a href={metadata.deep_link} className="px-4 py-2 rounded-md bg-cyan-600 text-black font-semibold">Open Pocket App</a>
          </div>
        )}

        {/* COD */}
        {session.provider === "cod" && !metadata.qr_url && (
          <div className="p-4 rounded-md bg-white/3 text-sm text-neutral-200">
            Cash on Delivery selected. An escrow entry has been created and will remain pending until delivery confirmation.
            <div className="mt-2"><span className="inline-block px-2 py-1 rounded-full bg-yellow-600 text-black text-xs">Pending Delivery</span></div>
          </div>
        )}

      </div>
    </div>
  );
}
