export enum TemplateType {
  EMAIL = 'email',
  PUSH = 'push',
  SMS = 'sms',
}

export interface ITemplate {
  id: number;
  template_key: string;
  name: string;
  type: TemplateType;
  language: string;
  subject: string;
  body: string;
  variables: string[];
  active_version: number;
  created_at: string;
  updated_at: string;
}

export interface IPaginationMeta {
  total: number;
  limit: number;
  page: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ITemplateResponse {
  success: boolean;
  data: ITemplate;
  message: string;
  meta: IPaginationMeta;
}

export interface ITemplateListResponse {
  success: boolean;
  data: ITemplate[];
  message: string;
  meta: IPaginationMeta;
}

export interface ITemplateValidation {
  valid: boolean;
  missing_variables: string[];
  extra_variables: string[];
}

export interface IRenderedTemplate {
  subject: string;
  body: string;
  variables_used: Record<string, string>;
}