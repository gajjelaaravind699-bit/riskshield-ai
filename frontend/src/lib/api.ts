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
