import React from "react";
import { PaymentMethod } from "@/types/payments";

interface Props {
  selected?: PaymentMethod;
  onSelect: (m: PaymentMethod) => void;
}

const methods: { key: PaymentMethod; title: string; desc: string; icon: string }[] = [
  { key: "al_kuraimi", title: "Al-Kuraimi (MFloos)", desc: "QR / local bank transfer support", icon: "💳" },
  { key: "al_najm", title: "Al-Najm", desc: "Fast local transfer checkout", icon: "🏦" },
  { key: "pocket", title: "Pocket Wallet", desc: "Deep-link mobile wallet", icon: "📱" },
  { key: "cod", title: "Cash on Delivery", desc: "Pay on delivery (escrow)", icon: "📦" },
];

export default function PaymentSelector({ selected, onSelect }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {methods.map((m) => (
        <button
          key={m.key}
          onClick={() => onSelect(m.key)}
          className={`p-4 rounded-xl backdrop-blur-md bg-gradient-to-br from-black/40 to-white/5 border border-white/5 flex items-start gap-3 hover:scale-[1.01] transition transform ${selected === m.key ? "ring-2 ring-cyan-400" : ""}`}
        >
          <div className="text-3xl">{m.icon}</div>
          <div className="text-left">
            <div className="font-semibold">{m.title}</div>
            <div className="text-sm text-neutral-400">{m.desc}</div>
          </div>
        </button>
      ))}
    </div>
  );
}
