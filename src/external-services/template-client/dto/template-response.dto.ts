import {
  IsString,
  IsNumber,
  IsArray,
  IsEnum,
  IsBoolean,
  IsOptional,
  ValidateNested,
} from 'class-validator';
import { Type } from 'class-transformer';

export enum TemplateType {
  EMAIL = 'email',
  PUSH = 'push',
  SMS = 'sms',
}

export class TemplateDataDto {
  @IsNumber()
  id: number;

  @IsString()
  template_key: string;

  @IsString()
  name: string;

  @IsEnum(TemplateType)
  type: TemplateType;

  @IsString()
  language: string;

  @IsString()
  subject: string;

  @IsString()
  body: string;

  @IsArray()
  @IsString({ each: true })
  variables: string[];

  @IsNumber()
  active_version: number;

  @IsString()
  created_at: string;

  @IsString()
  updated_at: string;
}

export class PaginationMetaDto {
  @IsNumber()
  total: number;

  @IsNumber()
  limit: number;

  @IsNumber()
  page: number;

  @IsNumber()
  total_pages: number;

  @IsBoolean()
  has_next: boolean;

  @IsBoolean()
  has_previous: boolean;
}

export class TemplateResponseDto {
  @IsBoolean()
  success: boolean;

  @ValidateNested()
  @Type(() => TemplateDataDto)
  data: TemplateDataDto;

  @IsString()
  message: string;

  @ValidateNested()
  @Type(() => PaginationMetaDto)
  meta: PaginationMetaDto;
}