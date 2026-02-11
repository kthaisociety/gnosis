// API service for communicating with the Gnosis gateway backend

import { authClient } from "@/lib/auth";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// ── Types matching backend models ──────────────────────────────────

export interface InferenceConfig {
  model_name: string;
  prompt: string;
  output_schema_name?: string;
  use_gpu?: boolean;
  dtype?: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  top_k?: number;
  api_key?: string;
  model_class?: string;
  device_map?: string;
  return_tensors?: string;
  padding?: string;
  attn_implementation?: string;
}

export interface VLMResponse {
  text?: string | null;
  format?: string | null;
  model_name?: string | null;
  inference_time_ms?: number | null;
  tokens_used?: number | null;
}

export interface HealthStatus {
  status: string;
  uptime_seconds: number;
  uptime_human: string;
  last_checked_utc: string;
}

export type Runner = "modal" | "local";

export interface ProcessRequest {
  file: File;
  runner: Runner;
  config: InferenceConfig;
}

// ── Auth helper ────────────────────────────────────────────────────

async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    const session = await authClient.getSession();
    const token = session?.data?.session?.token;
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
  } catch {
    // Session fetch failed — continue without auth header
  }
  return {};
}

// ── API Functions ──────────────────────────────────────────────────

export async function processImage(request: ProcessRequest): Promise<VLMResponse> {
  const authHeaders = await getAuthHeaders();

  const formData = new FormData();
  formData.append("file", request.file, request.file.name);
  formData.append("runner", request.runner);
  formData.append("config", JSON.stringify(request.config));

  const response = await fetch(`${API_BASE_URL}/process`, {
    method: "POST",
    body: formData,
    headers: {
      ...authHeaders,
      // Note: Do NOT set Content-Type — browser sets it with multipart boundary
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(
      response.status,
      errorBody.detail || `Request failed with status ${response.status}`
    );
  }

  return response.json();
}

export async function getHealthStatus(): Promise<HealthStatus> {
  const authHeaders = await getAuthHeaders();

  const response = await fetch(`${API_BASE_URL}/health/json`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      ...authHeaders,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, `Health check failed: ${response.statusText}`);
  }

  return response.json();
}

// ── Error class ────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
