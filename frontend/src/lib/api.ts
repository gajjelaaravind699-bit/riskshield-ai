/**
 * RiskShield AI API Client
 */

export interface DatabaseHealth {
  status: string;
  database?: string | null;
  error?: string | null;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
  timestamp: string;
  database?: DatabaseHealth | null;
}

export interface EntityRead {
  id: number;
  entity_type: string;
  entity_value: string;
  created_at: string;
}

export interface TransactionEntityRead {
  relationship_type: string;
  entity: EntityRead;
}

export interface TransactionRead {
  id: number;
  transaction_id: string;
  customer_id: string;
  amount: string;
  currency: string;
  status: string;
  payment_method: string;
  card_bin?: string | null;
  card_last4?: string | null;
  instrument_token?: string | null;
  upi_vpa?: string | null;
  device_id?: string | null;
  ip_address?: string | null;
  user_agent?: string | null;
  location_city?: string | null;
  location_country?: string | null;
  transacted_at: string;
  created_at: string;
  updated_at: string;
  entities: TransactionEntityRead[];
}

export interface TransactionCreateInput {
  transaction_id: string;
  customer_id: string;
  amount: string;
  currency?: string;
  status?: string;
  payment_method: string;
  card_bin?: string;
  card_last4?: string;
  instrument_token?: string;
  upi_vpa?: string;
  device_id?: string;
  ip_address?: string;
  user_agent?: string;
  location_city?: string;
  location_country?: string;
  transacted_at?: string;
}

export interface TransactionListResponse {
  items: TransactionRead[];
  total: number;
  page: number;
  page_size: number;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Fetch health status from backend API.
 */
export async function getHealthStatus(checkDb: boolean = false): Promise<HealthResponse> {
  const url = `${API_BASE_URL}/api/v1/health${checkDb ? "?check_db=true" : ""}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Ingest a single payment transaction.
 */
export async function createTransaction(data: TransactionCreateInput): Promise<TransactionRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/transactions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Network response was not ok" }));
    const errorMsg = typeof errorData.detail === "string" 
      ? errorData.detail 
      : Array.isArray(errorData.detail)
        ? errorData.detail.map((e: { msg?: string }) => e.msg).join(", ")
        : "Failed to ingest transaction";
    throw new Error(errorMsg);
  }

  return response.json();
}

/**
 * Retrieve paginated list of transactions with optional filtering.
 */
export async function getTransactions(params?: {
  skip?: number;
  limit?: number;
  customer_id?: string;
  status?: string;
  payment_method?: string;
}): Promise<TransactionListResponse> {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.set("skip", params.skip.toString());
  if (params?.limit !== undefined) query.set("limit", params.limit.toString());
  if (params?.customer_id) query.set("customer_id", params.customer_id);
  if (params?.status) query.set("status", params.status);
  if (params?.payment_method) query.set("payment_method", params.payment_method);

  const queryString = query.toString();
  const url = `${API_BASE_URL}/api/v1/transactions${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch transactions with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Retrieve a single transaction by ID including normalized entity relationships.
 */
export async function getTransactionById(transactionId: string): Promise<TransactionRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/transactions/${encodeURIComponent(transactionId)}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch transaction '${transactionId}' with status: ${response.status}`);
  }

  return response.json();
}
