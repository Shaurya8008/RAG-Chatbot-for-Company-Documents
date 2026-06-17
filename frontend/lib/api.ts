/**
 * API client for the RAG Chatbot backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Citation {
  index: number;
  document_title: string;
  section_title: string;
  parent_section: string;
  excerpt: string;
  document_id: string;
  relevance_score: number;
  permission_level: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  confidence: "high" | "medium" | "low" | "no_results";
  session_id: string;
  message_id: string;
  retrieval_metadata: Record<string, unknown>;
  generation_metadata: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations: Citation[];
  retrieval_metadata: Record<string, unknown>;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface DocumentInfo {
  id: string;
  title: string;
  filename: string;
  file_type: string;
  department: string;
  owner: string;
  permission_level: string;
  status: string;
  chunk_count: string;
  version: string;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  documents: {
    total: number;
    indexed: number;
    failed: number;
    pending: number;
  };
  users: { total: number };
  chat: {
    total_sessions: number;
    total_queries: number;
  };
  vector_store: {
    collection_name: string;
    total_chunks: number;
  };
  recent_queries: Array<{
    query: string;
    confidence: string;
    timestamp: string;
  }>;
}

export interface HealthStatus {
  status: string;
  services: {
    ollama_embeddings: { status: string; model: string };
    ollama_llm: { status: string; model: string };
    chromadb: { status: string; total_chunks: number };
  };
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      (error as { detail?: string }).detail || `API error: ${response.status}`
    );
  }

  return response.json();
}

// ── Chat API ──

export async function sendChatQuery(
  query: string,
  sessionId?: string,
  departmentFilter?: string
): Promise<ChatResponse> {
  return fetchAPI<ChatResponse>("/api/chat/query", {
    method: "POST",
    body: JSON.stringify({
      query,
      session_id: sessionId || null,
      department_filter: departmentFilter || null,
    }),
  });
}

export async function getChatSessions(): Promise<ChatSession[]> {
  return fetchAPI<ChatSession[]>("/api/chat/sessions");
}

export async function getSessionMessages(
  sessionId: string
): Promise<ChatMessage[]> {
  return fetchAPI<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`);
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetchAPI(`/api/chat/sessions/${sessionId}`, { method: "DELETE" });
}

// ── Documents API ──

export async function getDocuments(): Promise<DocumentInfo[]> {
  return fetchAPI<DocumentInfo[]>("/api/documents/");
}

export async function uploadDocument(
  file: File,
  title?: string,
  department?: string,
  permissionLevel?: string
): Promise<{ status: string; document: DocumentInfo }> {
  const formData = new FormData();
  formData.append("file", file);
  if (title) formData.append("title", title);
  if (department) formData.append("department", department);
  if (permissionLevel) formData.append("permission_level", permissionLevel);

  return fetchAPI("/api/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export async function ingestSampleData(): Promise<{
  status: string;
  documents_ingested: number;
  documents: DocumentInfo[];
}> {
  return fetchAPI("/api/documents/ingest-sample", { method: "POST" });
}

export async function deleteDocument(documentId: string): Promise<void> {
  await fetchAPI(`/api/documents/${documentId}`, { method: "DELETE" });
}

// ── Admin API ──

export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchAPI<DashboardStats>("/api/admin/dashboard");
}

export async function getHealthStatus(): Promise<HealthStatus> {
  return fetchAPI<HealthStatus>("/api/admin/health");
}

// ── Auth API ──

export async function login(
  email: string,
  password: string
): Promise<{ access_token: string; user: Record<string, string> }> {
  const result = await fetchAPI<{
    access_token: string;
    user: Record<string, string>;
  }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", result.access_token);
  }
  return result;
}

export async function register(
  email: string,
  name: string,
  password: string,
  role?: string
): Promise<{ access_token: string; user: Record<string, string> }> {
  const result = await fetchAPI<{
    access_token: string;
    user: Record<string, string>;
  }>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, name, password, role: role || "employee" }),
  });
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", result.access_token);
  }
  return result;
}
