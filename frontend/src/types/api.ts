export interface ApiError {
  detail: {
    error: string;
    message: string;
    field?: string;
    retry_after?: number;
    limit?: number;
    window?: number;
    device_id?: string;
    target?: string;
  };
}
