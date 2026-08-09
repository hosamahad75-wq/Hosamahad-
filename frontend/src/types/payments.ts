export type PaymentMethod = "al_kuraimi" | "al_najm" | "pocket" | "cod";

export interface CreatePaymentRequest {
  tenant_id: number;
  amount: number;
  currency: "USD" | "SAR" | "YER_SANAA" | "YER_ADEN";
  method: PaymentMethod;
  description?: string;
}

export interface CreatePaymentResponse {
  session_id: string;
  provider: string;
  next_action: string;
  metadata: Record<string, any>;
}

export interface VerifyPaymentRequest {
  session_id: string;
}

export interface VerifyPaymentResponse {
  session_id: string;
  status: "pending" | "paid" | "failed" | "cancelled";
  details: Record<string, any>;
}
