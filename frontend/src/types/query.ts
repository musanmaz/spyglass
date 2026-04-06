export interface QueryRequest {
  query_type: string;
  target: string;
  device_ids?: string[];
}

export interface QueryResultItem {
  device_id: string;
  device_name: string;
  platform: string;
  location: Record<string, unknown>;
  network: Record<string, unknown>;
  query_type: string;
  target: string;
  output: string;
  status: string;
  response_time_ms: number;
  cached?: boolean;
  error?: string;
}

export interface QueryResponse {
  request_id: string;
  cached: boolean;
  timestamp: string;
  results: QueryResultItem[];
}
