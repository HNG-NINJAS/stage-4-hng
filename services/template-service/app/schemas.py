"""
Pydantic schemas for request/response validation (snake_case)
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ==================== Standard Response Format ====================

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int
    limit: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ApiResponse(BaseModel):
    """Standard API response format"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: str
    meta: PaginationMeta


# ==================== Template Schemas ====================

class TemplateVersionBase(BaseModel):
    """Base template version schema"""
    version: str
    subject: Optional[str] = None
    body: str
    variables: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TemplateVersionCreate(TemplateVersionBase):
    """Create template version"""
    pass


class TemplateVersionResponse(TemplateVersionBase):
    """Template version response"""
    id: UUID
    template_id: UUID
    is_current: bool
    created_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class TemplateTranslationBase(BaseModel):
    """Base translation schema"""
    language_code: str = Field(..., min_length=2, max_length=10)
    subject: Optional[str] = Field(None, max_length=500)
    body: str = Field(..., min_length=1)

    @validator('language_code')
    def validate_language_code(cls, v):
        """Ensure lowercase language code"""
        return v.lower().strip()


class TemplateTranslationCreate(TemplateTranslationBase):
    """Create translation"""
    pass


class TemplateTranslationResponse(TemplateTranslationBase):
    """Translation response"""
    id: UUID
    template_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateBase(BaseModel):
    """Base template schema"""
    template_id: str = Field(..., min_length=3, max_length=100)
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    type: str = Field(..., pattern="^(email|push|sms)$")
    category: Optional[str] = Field(None, max_length=100)

    @validator('template_id')
    def validate_template_id(cls, v):
        """Ensure valid template ID format"""
        # Allow letters, numbers, underscore, hyphen
        import re
        if not re.match(r'^[a-z0-9_-]+$', v.lower()):
            raise ValueError('template_id must contain only lowercase letters, numbers, underscore, or hyphen')
        return v.lower()


class TemplateCreate(TemplateBase):
    """Create template"""
    subject: Optional[str] = Field(None, max_length=500)
    body: str = Field(..., min_length=1)
    variables: Optional[List[str]] = Field(default_factory=list)
    language_code: str = Field(default="en", min_length=2, max_length=10)


class TemplateUpdate(BaseModel):
    """Update template"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    subject: Optional[str] = Field(None, max_length=500)
    body: Optional[str] = Field(None, min_length=1)
    variables: Optional[List[str]] = None


class TemplateResponse(TemplateBase):
    """Template response"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    current_version: Optional[TemplateVersionResponse] = None

    class Config:
        from_attributes = True


class TemplateDetailResponse(TemplateResponse):
    """Detailed template response with versions and translations"""
    versions: List[TemplateVersionResponse] = []
    translations: List[TemplateTranslationResponse] = []


class TemplateListResponse(BaseModel):
    """List of templates"""
    templates: List[TemplateResponse]
    total: int


# ==================== Render Schemas ====================

class RenderRequest(BaseModel):
    """Template render request"""
    data: Dict[str, Any] = Field(..., description="Variables to substitute in template")
    language_code: Optional[str] = Field(default="en", min_length=2, max_length=10)

    @validator('data')
    def validate_data(cls, v):
        """Ensure data is not empty"""
        if not v:
            raise ValueError('data cannot be empty')
        return v


class RenderResponse(BaseModel):
    """Template render response"""
    subject: Optional[str] = None
    body: str
    variables_used: List[str]