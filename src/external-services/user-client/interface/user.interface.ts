export interface IQuietHours {
  start: string;
  end: string;
}

export interface IUserPreferences {
  email_enabled: boolean;
  push_enabled: boolean;
  sms_enabled: boolean;
  language: string;
  timezone: string;
  quiet_hours?: IQuietHours;
}

export interface IUser {
  user_id: string;
  email: string;
  phone?: string;
  preferences: IUserPreferences;
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

export interface IUserResponse {
  success: boolean;
  data: IUser;
  message: string;
  meta: IPaginationMeta;
}

export interface IUserListResponse {
  success: boolean;
  data: IUser[];
  message: string;
  meta: IPaginationMeta;
}