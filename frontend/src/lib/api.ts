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

export interface TransactionSummaryRead {
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
  transacted_at: string;
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

// Phase 3: Graph & Pattern Analysis Types
export interface FindingEntityRead {
  id: number;
  role: string;
  entity: EntityRead;
}

export interface FindingTransactionRead {
  id: number;
  transaction: TransactionSummaryRead;
}

export interface FindingRead {
  id: number;
  finding_id: string;
  analysis_run_id: number;
  finding_type: string;
  severity: string;
  title: string;
  explanation: string;
  fingerprint: string;
  evidence_payload: Record<string, unknown>;
  created_at: string;
  related_entities: FindingEntityRead[];
  related_transactions: FindingTransactionRead[];
}

export interface FindingListResponse {
  items: FindingRead[];
  total: number;
  page: number;
  page_size: number;
}

export interface AnalysisConfigInput {
  shared_instrument_threshold?: number;
  shared_device_threshold?: number;
  shared_ip_threshold?: number;
  velocity_burst_count?: number;
  velocity_window_minutes?: number;
  failure_burst_count?: number;
  failure_window_minutes?: number;
}

export interface AnalysisRunRead {
  id: number;
  run_id: string;
  status: string;
  total_transactions_analyzed: number;
  findings_count: number;
  config_hash: string;
  completed_at?: string | null;
  created_at: string;
  findings: FindingRead[];
}

export interface AnalysisRunListResponse {
  items: AnalysisRunRead[];
  total: number;
  page: number;
  page_size: number;
}

// Phase 4: Risk Scoring & Decision Support Types
export interface RulesetConfigInput {
  ruleset_version?: string;
  shared_instrument_weight?: number;
  shared_device_weight?: number;
  shared_ip_weight?: number;
  velocity_burst_weight?: number;
  failure_burst_weight?: number;
  base_score?: number;
  max_score?: number;
}

export interface DecisionPolicyConfigInput {
  decision_policy_version?: string;
  review_threshold?: number;
  block_threshold?: number;
}

export interface AssessmentEvaluationRequestInput {
  ruleset?: RulesetConfigInput;
  policy?: DecisionPolicyConfigInput;
}

export interface RuleContributionRead {
  rule_name: string;
  finding_type: string;
  weight: number;
  triggered: boolean;
  points_contributed: number;
  description: string;
  finding_ids: string[];
}

export interface AssessmentRead {
  id: number;
  assessment_id: string;
  transaction_id: number;
  score: number;
  risk_level: string;
  recommendation: string;
  explanation: string;
  ruleset_version: string;
  decision_policy_version: string;
  rule_contributions: RuleContributionRead[];
  evidence_summary: Record<string, unknown>;
  action_executed: boolean;
  action_disclaimer: string;
  created_at: string;
  transaction?: TransactionSummaryRead | null;
}

export interface AssessmentListResponse {
  items: AssessmentRead[];
  total: number;
  page: number;
  page_size: number;
}

export interface AssessmentBatchResponse {
  total_evaluated: number;
  allow_count: number;
  review_count: number;
  block_count: number;
  ruleset_version: string;
  decision_policy_version: string;
  action_disclaimer: string;
  items: AssessmentRead[];
}

// Phase 5: Analyst Case Management Types
export interface CaseNoteRead {
  id: number;
  note_id: string;
  author: string;
  content: string;
  created_at: string;
}

export interface CaseAuditEventRead {
  id: number;
  event_id: string;
  event_type: string;
  actor: string;
  from_state?: string | null;
  to_state?: string | null;
  event_details: Record<string, unknown>;
  created_at: string;
}

export interface CaseRead {
  id: number;
  case_id: string;
  title: string;
  description?: string | null;
  status: string;
  priority: string;
  assigned_to?: string | null;
  transaction_id: number;
  assessment_id?: number | null;
  disposition?: string | null;
  disposition_rationale?: string | null;
  disposition_at?: string | null;
  disposition_by?: string | null;
  created_at: string;
  updated_at: string;
  transaction?: TransactionSummaryRead | null;
  assessment?: AssessmentRead | null;
  notes: CaseNoteRead[];
  audit_events: CaseAuditEventRead[];
}

export interface CaseListResponse {
  items: CaseRead[];
  total: number;
  page: number;
  page_size: number;
}

export interface CaseCreateInput {
  transaction_id: string;
  title: string;
  description?: string;
  priority?: string;
  assigned_to?: string;
  actor?: string;
}

export interface CaseFromAssessmentInput {
  title?: string;
  description?: string;
  priority?: string;
  assigned_to?: string;
  actor?: string;
}

export interface CaseStatusUpdateInput {
  status: string;
  actor: string;
  reason?: string;
}

export interface CaseAssignmentUpdateInput {
  assigned_to?: string | null;
  actor: string;
}

export interface CasePriorityUpdateInput {
  priority: string;
  actor: string;
}

export interface CaseNoteCreateInput {
  content: string;
  author: string;
}

export interface CaseDispositionCreateInput {
  disposition: string;
  rationale: string;
  actor: string;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Build request headers with optional API Key authentication for backend RBAC.
 */
export function getAuthHeaders(customHeaders?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...customHeaders,
  };
  const apiKey = process.env.NEXT_PUBLIC_API_KEY || "rs_analyst_key_dev";
  if (apiKey && !headers["X-API-Key"]) {
    headers["X-API-Key"] = apiKey;
  }
  return headers;
}

/**
 * Fetch health status from backend API.
 */
export async function getHealthStatus(checkDb: boolean = false): Promise<HealthResponse> {
  const url = `${API_BASE_URL}/api/v1/health${checkDb ? "?check_db=true" : ""}`;
  const response = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
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
    headers: getAuthHeaders(),
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
    headers: getAuthHeaders(),
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
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch transaction '${transactionId}' with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Trigger graph and pattern analysis execution.
 */
export async function triggerAnalysis(config?: AnalysisConfigInput): Promise<AnalysisRunRead> {
  const body = config ? { config } : {};
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/run`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to trigger analysis" }));
    throw new Error(errorData.detail || "Analysis trigger failed");
  }

  return response.json();
}

/**
 * Retrieve paginated list of analysis execution runs.
 */
export async function getAnalysisRuns(params?: {
  skip?: number;
  limit?: number;
}): Promise<AnalysisRunListResponse> {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.set("skip", params.skip.toString());
  if (params?.limit !== undefined) query.set("limit", params.limit.toString());

  const queryString = query.toString();
  const url = `${API_BASE_URL}/api/v1/analysis/runs${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch analysis runs with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Retrieve paginated list of findings with optional filters.
 */
export async function getFindings(params?: {
  skip?: number;
  limit?: number;
  finding_type?: string;
  severity?: string;
  run_id?: string;
}): Promise<FindingListResponse> {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.set("skip", params.skip.toString());
  if (params?.limit !== undefined) query.set("limit", params.limit.toString());
  if (params?.finding_type) query.set("finding_type", params.finding_type);
  if (params?.severity) query.set("severity", params.severity);
  if (params?.run_id) query.set("run_id", params.run_id);

  const queryString = query.toString();
  const url = `${API_BASE_URL}/api/v1/analysis/findings${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch findings with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Retrieve a single finding by ID with full explainable evidence payload.
 */
export async function getFindingById(findingId: string): Promise<FindingRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/findings/${encodeURIComponent(findingId)}`, {
    method: "GET",
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch finding '${findingId}' with status: ${response.status}`);
  }

  return response.json();
}

// Phase 4: Risk Scoring & Decision-Support Methods

/**
 * Evaluate deterministic risk assessment for a single transaction.
 */
export async function evaluateTransaction(
  transactionId: string,
  payload?: AssessmentEvaluationRequestInput
): Promise<AssessmentRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assessments/evaluate/${encodeURIComponent(transactionId)}`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload || {}),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Assessment evaluation failed" }));
    throw new Error(errorData.detail || "Failed to evaluate transaction risk");
  }

  return response.json();
}

/**
 * Evaluate deterministic risk assessments across all persisted transactions.
 */
export async function evaluateAllTransactions(
  payload?: AssessmentEvaluationRequestInput
): Promise<AssessmentBatchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assessments/evaluate-all`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload || {}),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Batch assessment evaluation failed" }));
    throw new Error(errorData.detail || "Failed to execute batch risk assessment");
  }

  return response.json();
}

/**
 * Retrieve paginated list of risk assessments with optional filters.
 */
export async function getAssessments(params?: {
  skip?: number;
  limit?: number;
  recommendation?: string;
  risk_level?: string;
  customer_id?: string;
  transaction_id?: string;
}): Promise<AssessmentListResponse> {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.set("skip", params.skip.toString());
  if (params?.limit !== undefined) query.set("limit", params.limit.toString());
  if (params?.recommendation) query.set("recommendation", params.recommendation);
  if (params?.risk_level) query.set("risk_level", params.risk_level);
  if (params?.customer_id) query.set("customer_id", params.customer_id);
  if (params?.transaction_id) query.set("transaction_id", params.transaction_id);

  const queryString = query.toString();
  const url = `${API_BASE_URL}/api/v1/assessments${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch assessments with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Retrieve a single assessment by ID.
 */
export async function getAssessmentById(assessmentId: string): Promise<AssessmentRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assessments/${encodeURIComponent(assessmentId)}`, {
    method: "GET",
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch assessment '${assessmentId}' with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Retrieve assessment for a specific transaction ID.
 */
export async function getAssessmentByTransactionId(transactionId: string): Promise<AssessmentRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assessments/transaction/${encodeURIComponent(transactionId)}`, {
    method: "GET",
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch assessment for transaction '${transactionId}' with status: ${response.status}`);
  }

  return response.json();
}

// Phase 5: Analyst Case Management Methods

/**
 * Create a case manually.
 */
export async function createCase(payload: CaseCreateInput): Promise<CaseRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to create case" }));
    throw new Error(errorData.detail || "Case creation failed");
  }

  return response.json();
}

/**
 * Create a case directly from an assessment.
 */
export async function createCaseFromAssessment(
  assessmentId: string,
  payload?: CaseFromAssessmentInput
): Promise<CaseRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases/from-assessment/${encodeURIComponent(assessmentId)}`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload || {}),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to create case from assessment" }));
    throw new Error(errorData.detail || "Case creation from assessment failed");
  }

  return response.json();
}

/**
 * Retrieve paginated list of cases in queue.
 */
export async function getCases(params?: {
  skip?: number;
  limit?: number;
  status?: string;
  priority?: string;
  assigned_to?: string;
  disposition?: string;
  transaction_id?: string;
}): Promise<CaseListResponse> {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.set("skip", params.skip.toString());
  if (params?.limit !== undefined) query.set("limit", params.limit.toString());
  if (params?.status) query.set("status", params.status);
  if (params?.priority) query.set("priority", params.priority);
  if (params?.assigned_to) query.set("assigned_to", params.assigned_to);
  if (params?.disposition) query.set("disposition", params.disposition);
  if (params?.transaction_id) query.set("transaction_id", params.transaction_id);

  const queryString = query.toString();
  const url = `${API_BASE_URL}/api/v1/cases${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch cases with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Retrieve a single case by ID with full notes and audit events.
 */
export async function getCaseById(caseId: string): Promise<CaseRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases/${encodeURIComponent(caseId)}`, {
    method: "GET",
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch case '${caseId}' with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Update case status.
 */
export async function updateCaseStatus(caseId: string, payload: CaseStatusUpdateInput): Promise<CaseRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases/${encodeURIComponent(caseId)}/status`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Status update failed" }));
    throw new Error(errorData.detail || "Status update failed");
  }

  return response.json();
}

/**
 * Update case assignment.
 */
export async function updateCaseAssignment(caseId: string, payload: CaseAssignmentUpdateInput): Promise<CaseRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases/${encodeURIComponent(caseId)}/assignment`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Assignment update failed" }));
    throw new Error(errorData.detail || "Assignment update failed");
  }

  return response.json();
}

/**
 * Update case priority.
 */
export async function updateCasePriority(caseId: string, payload: CasePriorityUpdateInput): Promise<CaseRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases/${encodeURIComponent(caseId)}/priority`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Priority update failed" }));
    throw new Error(errorData.detail || "Priority update failed");
  }

  return response.json();
}

/**
 * Append a note to a case.
 */
export async function addCaseNote(caseId: string, payload: CaseNoteCreateInput): Promise<CaseNoteRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases/${encodeURIComponent(caseId)}/notes`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Note creation failed" }));
    throw new Error(errorData.detail || "Note creation failed");
  }

  return response.json();
}

/**
 * Record analyst disposition.
 */
export async function recordCaseDisposition(caseId: string, payload: CaseDispositionCreateInput): Promise<CaseRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cases/${encodeURIComponent(caseId)}/disposition`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Disposition recording failed" }));
    throw new Error(errorData.detail || "Disposition recording failed");
  }

  return response.json();
}
