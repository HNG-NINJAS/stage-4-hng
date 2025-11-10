"""
Template CRUD API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import logging

from app.database import get_db
from app.services.template_service import TemplateService
from app.schemas import (
    TemplateCreate, TemplateUpdate, TemplateResponse, 
    TemplateDetailResponse, RenderRequest, RenderResponse,
    TemplateTranslationCreate, TemplateVersionResponse
)
from app.utils.response import success_response, error_response
from app.api.metrics import track_operation, track_render_time
from app.models import TemplateVersion

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/templates", tags=["Templates"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new notification template
    
    - **template_id**: Unique identifier (e.g., 'welcome_email')
    - **name**: Human-readable name
    - **type**: email, push, or sms
    - **body**: Template content with {{variables}}
    - **subject**: Email subject (optional for email templates)
    - **language_code**: Initial language (default: 'en')
    """
    try:
        service = TemplateService(db)
        template = service.create_template(template_data)
        
        # Get current version for response
        current_version = db.query(TemplateVersion).filter(
            TemplateVersion.template_id == template.id,
            TemplateVersion.is_current == True
        ).first()
        
        response_data = TemplateResponse(
            id=template.id,
            template_id=template.template_id,
            name=template.name,
            description=template.description,
            type=template.type,
            category=template.category,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
            current_version=current_version
        )
        
        track_operation("create", "success")
        logger.info(f"Template '{template.template_id}' created successfully")
        
        return success_response(
            message="Template created successfully",
            data=response_data.model_dump(),
            total=1
        )
    
    except ValueError as e:
        track_operation("create", "error")
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        track_operation("create", "error")
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("", status_code=status.HTTP_200_OK)
def list_templates(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, pattern="^(email|push|sms)$", description="Filter by type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    db: Session = Depends(get_db)
):
    """
    List all templates with pagination and filters
    
    Supports filtering by:
    - **type**: email, push, or sms
    - **category**: Template category
    - **search**: Search term for name/description
    """
    try:
        service = TemplateService(db)
        skip = (page - 1) * limit
        
        templates, total = service.list_templates(
            skip=skip,
            limit=limit,
            type=type,
            category=category,
            search=search
        )
        
        # Build response with current versions
        response_data = []
        for template in templates:
            current_version = db.query(TemplateVersion).filter(
                TemplateVersion.template_id == template.id,
                TemplateVersion.is_current == True
            ).first()
            
            template_response = TemplateResponse(
                id=template.id,
                template_id=template.template_id,
                name=template.name,
                description=template.description,
                type=template.type,
                category=template.category,
                is_active=template.is_active,
                created_at=template.created_at,
                updated_at=template.updated_at,
                current_version=current_version
            )
            response_data.append(template_response.model_dump())
        
        track_operation("list", "success")
        
        return success_response(
            message="Templates retrieved successfully",
            data=response_data,
            total=total,
            limit=limit,
            page=page
        )
    
    except Exception as e:
        track_operation("list", "error")
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{template_id}", status_code=status.HTTP_200_OK)
def get_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific template by template_id with all versions and translations
    """
    try:
        service = TemplateService(db)
        template = service.get_template(template_id)
        
        if not template:
            track_operation("get", "not_found")
            return error_response(
                message=f"Template with id '{template_id}' not found",
                error="TEMPLATE_NOT_FOUND"
            )
        
        # Build detailed response
        response_data = TemplateDetailResponse(
            id=template.id,
            template_id=template.template_id,
            name=template.name,
            description=template.description,
            type=template.type,
            category=template.category,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
            current_version=next((v for v in template.versions if v.is_current), None),
            versions=template.versions,
            translations=template.translations
        )
        
        track_operation("get", "success")
        
        return success_response(
            message="Template retrieved successfully",
            data=response_data.model_dump(),
            total=1
        )
    
    except Exception as e:
        track_operation("get", "error")
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{template_id}", status_code=status.HTTP_200_OK)
def update_template(
    template_id: str,
    update_data: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a template (creates new version if content changes)
    
    If body or subject is updated, a new version is automatically created
    """
    try:
        service = TemplateService(db)
        template = service.update_template(template_id, update_data)
        
        if not template:
            track_operation("update", "not_found")
            return error_response(
                message=f"Template with id '{template_id}' not found",
                error="TEMPLATE_NOT_FOUND"
            )
        
        # Get current version
        current_version = db.query(TemplateVersion).filter(
            TemplateVersion.template_id == template.id,
            TemplateVersion.is_current == True
        ).first()
        
        response_data = TemplateResponse(
            id=template.id,
            template_id=template.template_id,
            name=template.name,
            description=template.description,
            type=template.type,
            category=template.category,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
            current_version=current_version
        )
        
        track_operation("update", "success")
        logger.info(f"Template '{template_id}' updated successfully")
        
        return success_response(
            message="Template updated successfully",
            data=response_data.model_dump(),
            total=1
        )
    
    except ValueError as e:
        track_operation("update", "error")
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        track_operation("update", "error")
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{template_id}", status_code=status.HTTP_200_OK)
def delete_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft delete a template (sets is_active to False)
    
    Template remains in database but won't appear in listings
    """
    try:
        service = TemplateService(db)
        success = service.delete_template(template_id)
        
        if not success:
            track_operation("delete", "not_found")
            return error_response(
                message=f"Template with id '{template_id}' not found",
                error="TEMPLATE_NOT_FOUND"
            )
        
        track_operation("delete", "success")
        logger.info(f"Template '{template_id}' deleted successfully")
        
        return success_response(
            message="Template deleted successfully",
            data={"template_id": template_id, "deleted": True}
        )
    
    except Exception as e:
        track_operation("delete", "error")
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{template_id}/render", status_code=status.HTTP_200_OK)
def render_template(
    template_id: str,
    render_request: RenderRequest,
    db: Session = Depends(get_db)
):
    """
    Render a template with provided data
    
    Substitutes variables in the template with actual values
    
    Example request body:
```json
    {
        "data": {
            "name": "John Doe",
            "verification_link": "https://example.com/verify/123"
        },
        "language_code": "en"
    }
```
    """
    start_time = time.time()
    
    try:
        service = TemplateService(db)
        result = service.render_template(
            template_id,
            render_request.data,
            render_request.language_code or "en"
        )
        
        if not result:
            track_operation("render", "not_found")
            return error_response(
                message=f"Template '{template_id}' not found or no translation available",
                error="TEMPLATE_NOT_FOUND"
            )
        
        response_data = RenderResponse(
            subject=result["subject"],
            body=result["body"],
            variables_used=result["variables_used"]
        )
        
        # Track render time
        duration = time.time() - start_time
        track_render_time(template_id, duration)
        track_operation("render", "success")
        
        logger.info(f"Template '{template_id}' rendered in {duration:.3f}s")
        
        return success_response(
            message="Template rendered successfully",
            data=response_data.model_dump(),
            total=1
        )
    
    except ValueError as e:
        track_operation("render", "error")
        logger.error(f"Render validation error: {str(e)}")
        return error_response(
            message=str(e),
            error="MISSING_VARIABLES"
        )
    except Exception as e:
        track_operation("render", "error")
        logger.error(f"Error rendering template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{template_id}/translations", status_code=status.HTTP_201_CREATED)
def add_translation(
    template_id: str,
    translation_data: TemplateTranslationCreate,
    db: Session = Depends(get_db)
):
    """
    Add or update a translation for a template
    
    Allows supporting multiple languages for the same template
    """
    try:
        service = TemplateService(db)
        translation = service.add_translation(
            template_id,
            translation_data.language_code,
            translation_data.subject,
            translation_data.body
        )
        
        if not translation:
            track_operation("add_translation", "not_found")
            return error_response(
                message=f"Template with id '{template_id}' not found",
                error="TEMPLATE_NOT_FOUND"
            )
        
        track_operation("add_translation", "success")
        logger.info(f"Translation '{translation_data.language_code}' added to template '{template_id}'")
        
        return success_response(
            message="Translation added successfully",
            data={
                "id": str(translation.id),
                "template_id": template_id,
                "language_code": translation.language_code,
                "created_at": translation.created_at.isoformat()
            },
            total=1
        )
    
    except Exception as e:
        track_operation("add_translation", "error")
        logger.error(f"Error adding translation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{template_id}/versions", status_code=status.HTTP_200_OK)
def get_template_versions(
    template_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all versions of a template
    
    Returns version history ordered by creation date (newest first)
    """
    try:
        service = TemplateService(db)
        template = service.get_template(template_id)
        
        if not template:
            track_operation("get_versions", "not_found")
            return error_response(
                message=f"Template with id '{template_id}' not found",
                error="TEMPLATE_NOT_FOUND"
            )
        
        versions = service.get_template_versions(template_id)
        
        response_data = [{
            "id": str(v.id),
            "version": v.version,
            "subject": v.subject,
            "body": v.body,
            "variables": v.variables,
            "is_current": v.is_current,
            "created_at": v.created_at.isoformat(),
            "created_by": v.created_by,
            "template_metadata": v.template_metadata
        } for v in versions]
        
        track_operation("get_versions", "success")
        
        return success_response(
            message="Template versions retrieved successfully",
            data=response_data,
            total=len(versions)
        )
    
    except Exception as e:
        track_operation("get_versions", "error")
        logger.error(f"Error getting template versions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/stats/summary", status_code=status.HTTP_200_OK)
def get_statistics(db: Session = Depends(get_db)):
    """
    Get template service statistics
    
    Returns counts of templates, versions, and translations
    """
    try:
        service = TemplateService(db)
        stats = service.get_statistics()
        
        return success_response(
            message="Statistics retrieved successfully",
            data=stats
        )
    
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )