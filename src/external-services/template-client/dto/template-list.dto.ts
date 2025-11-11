import { IsBoolean, IsString, IsArray, ValidateNested } from 'class-validator';
import { Type } from 'class-transformer';
import { TemplateDataDto, PaginationMetaDto } from './template-response.dto';

export class TemplateListResponseDto {
  @IsBoolean()
  success: boolean;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => TemplateDataDto)
  data: TemplateDataDto[];

  @IsString()
  message: string;

  @ValidateNested()
  @Type(() => PaginationMetaDto)
  meta: PaginationMetaDto;
}