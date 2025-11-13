// ============================================================================
// src/common/dto/response.dto.ts - STANDARD RESPONSE
// ============================================================================
export interface PaginationMeta {
  total: number;
  limit: number;
  page: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export class ApiResponse<T = any> {
  success: boolean;
  data: T | null;
  error: string | null;
  message: string;
  meta: PaginationMeta;

  constructor(
    success: boolean,
    message: string,
    data: T | null = null,
    error: string | null = null,
    meta: PaginationMeta = {
      total: 0,
      limit: 0,
      page: 0,
      total_pages: 0,
      has_next: false,
      has_previous: false,
    },
  ) {
    this.success = success;
    this.data = data;
    this.error = error;
    this.message = message;
    this.meta = meta;
  }
}
