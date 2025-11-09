"""
Template service - Business logic layer
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
import logging

from app.models import Template, TemplateVersion, TemplateTranslation
from app.schemas import TemplateCreate, TemplateUpdate
from app.utils.renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for template operations"""
    
    def __init__(self, db: Session):
        """
        Initialize template service
        
        Args:
            db: Database session
        """
        self.db = db
        self.renderer = TemplateRenderer()
    
    def create_template(self, template_data: TemplateCreate) -> Template:
        """
        Create a new template with initial version and translation
        
        Args:
            template_data: Template creation data
            
        Returns:
            Created template
            
        Raises:
            ValueError: If template_id already exists
        """
        # Check if template_id already exists
        existing = self.db.query(Template).filter(
            Template.template_id == template_data.template_id
        ).first()
        
        if existing:
            logger.warning(f"Template ID '{template_data.template_id}' already exists")
            raise ValueError(f"Template with ID '{template_data.template_id}' already exists")
        
        # Extract variables from body and subject
        variables = self.renderer.extract_variables(template_data.body)
        if template_data.subject:
            subject_vars = self.renderer.extract_variables(template_data.subject)
            variables.extend(subject_vars)
        variables = list(set(variables))  # Remove duplicates
        
        logger.info(f"Creating template '{template_data.template_id}' with {len(variables)} variables")
        
        # Create template
        template = Template(
            template_id=template_data.template_id,
            name=template_data.name,
            description=template_data.description,
            type=template_data.type,
            category=template_data.category
        )
        self.db.add(template)
        self.db.flush()  # Get the template ID
        
        # Create initial version (1.0.0)
        version = TemplateVersion(
            template_id=template.id,
            version="1.0.0",
            subject=template_data.subject,
            body=template_data.body,
            variables=variables,
            is_current=True,
            metadata={"initial_version": True}
        )
        self.db.add(version)
        
        # Create initial translation
        translation = TemplateTranslation(
            template_id=template.id,
            language_code=template_data.language_code,
            subject=template_data.subject,
            body=template_data.body
        )
        self.db.add(translation)
        
        self.db.commit()
        self.db.refresh(template)
        
        logger.info(f"Template '{template_data.template_id}' created successfully")
        return template
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """
        Get template by template_id
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template if found, None otherwise
        """
        return self.db.query(Template).filter(
            and_(
                Template.template_id == template_id,
                Template.is_active == True
            )
        ).first()
    
    def get_template_by_uuid(self, uuid: UUID) -> Optional[Template]:
        """
        Get template by UUID
        
        Args:
            uuid: Template UUID
            
        Returns:
            Template if found, None otherwise
        """
        return self.db.query(Template).filter(Template.id == uuid).first()
    
    def list_templates(
        self, 
        skip: int = 0, 
        limit: int = 10,
        type: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> Tuple[List[Template], int]:
        """
        List templates with pagination and filters
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            type: Filter by template type
            category: Filter by category
            search: Search in name or description
            is_active: Filter by active status
            
        Returns:
            Tuple of (templates list, total count)
        """
        query = self.db.query(Template)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Template.is_active == is_active)
        
        if type:
            query = query.filter(Template.type == type)
        
        if category:
            query = query.filter(Template.category == category)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Template.name.ilike(search_pattern),
                    Template.description.ilike(search_pattern),
                    Template.template_id.ilike(search_pattern)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and sorting
        templates = query.order_by(Template.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.debug(f"Retrieved {len(templates)} templates (total: {total})")
        return templates, total
    
    def update_template(
        self, 
        template_id: str, 
        update_data: TemplateUpdate
    ) -> Optional[Template]:
        """
        Update template and create new version if content changes
        
        Args:
            template_id: Template identifier
            update_data: Update data
            
        Returns:
            Updated template if found, None otherwise
        """
        template = self.get_template(template_id)
        if not template:
            logger.warning(f"Template '{template_id}' not found for update")
            return None
        
        logger.info(f"Updating template '{template_id}'")
        
        # Update basic fields
        if update_data.name is not None:
            template.name = update_data.name
        
        if update_data.description is not None:
            template.description = update_data.description
        
        if update_data.is_active is not None:
            template.is_active = update_data.is_active
        
        # If body or subject changes, create new version
        content_changed = update_data.body is not None or update_data.subject is not None
        
        if content_changed:
            # Get current version
            current_version = self.db.query(TemplateVersion).filter(
                and_(
                    TemplateVersion.template_id == template.id,
                    TemplateVersion.is_current == True
                )
            ).first()
            
            if current_version:
                # Mark current version as not current
                current_version.is_current = False
                
                # Parse version and increment patch number
                try:
                    major, minor, patch = map(int, current_version.version.split('.'))
                    new_version_str = f"{major}.{minor}.{patch + 1}"
                except ValueError:
                    # Fallback if version parsing fails
                    new_version_str = "1.0.1"
                
                # Use updated content or keep existing
                new_body = update_data.body if update_data.body is not None else current_version.body
                new_subject = update_data.subject if update_data.subject is not None else current_version.subject
                
                # Extract variables
                variables = self.renderer.extract_variables(new_body)
                if new_subject:
                    subject_vars = self.renderer.extract_variables(new_subject)
                    variables.extend(subject_vars)
                variables = list(set(variables))
                
                # Create new version
                new_version = TemplateVersion(
                    template_id=template.id,
                    version=new_version_str,
                    subject=new_subject,
                    body=new_body,
                    variables=variables,
                    is_current=True,
                    metadata={"updated_from": current_version.version}
                )
                self.db.add(new_version)
                
                logger.info(f"Created new version {new_version_str} for template '{template_id}'")
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def delete_template(self, template_id: str) -> bool:
        """
        Soft delete template (set is_active to False)
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if deleted, False if not found
        """
        template = self.get_template(template_id)
        if not template:
            logger.warning(f"Template '{template_id}' not found for deletion")
            return False
        
        template.is_active = False
        self.db.commit()
        
        logger.info(f"Template '{template_id}' soft deleted")
        return True
    
    def render_template(
        self, 
        template_id: str, 
        data: Dict[str, Any],
        language_code: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Render template with provided data
        
        Args:
            template_id: Template identifier
            data: Variables to substitute
            language_code: Language code for translation
            
        Returns:
            Rendered template dict with subject, body, and variables_used
            
        Raises:
            ValueError: If required variables are missing
        """
        template = self.get_template(template_id)
        if not template:
            logger.warning(f"Template '{template_id}' not found for rendering")
            return None
        
        # Get translation for requested language
        translation = self.db.query(TemplateTranslation).filter(
            and_(
                TemplateTranslation.template_id == template.id,
                TemplateTranslation.language_code == language_code,
                TemplateTranslation.is_active == True
            )
        ).first()
        
        # Fallback to English if translation not found
        if not translation:
            logger.info(f"Translation for '{language_code}' not found, falling back to 'en'")
            translation = self.db.query(TemplateTranslation).filter(
                and_(
                    TemplateTranslation.template_id == template.id,
                    TemplateTranslation.language_code == "en",
                    TemplateTranslation.is_active == True
                )
            ).first()
        
        if not translation:
            logger.error(f"No translation found for template '{template_id}'")
            return None
        
        # Validate variables
        is_valid, missing = self.renderer.validate_variables(translation.body, data)
        if not is_valid:
            error_msg = f"Missing required variables: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Render body
        rendered_body = self.renderer.render(translation.body, data)
        
        # Render subject if exists
        rendered_subject = None
        if translation.subject:
            # Validate subject variables
            is_valid, missing = self.renderer.validate_variables(translation.subject, data)
            if not is_valid:
                error_msg = f"Missing required variables in subject: {', '.join(missing)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            rendered_subject = self.renderer.render(translation.subject, data)
        
        # Get variables used
        variables_used = self.renderer.extract_variables(translation.body)
        if translation.subject:
            subject_vars = self.renderer.extract_variables(translation.subject)
            variables_used.extend(subject_vars)
        variables_used = list(set(variables_used))
        
        logger.info(f"Template '{template_id}' rendered successfully")
        
        return {
            "subject": rendered_subject,
            "body": rendered_body,
            "variables_used": variables_used
        }
    
    def add_translation(
        self, 
        template_id: str, 
        language_code: str,
        subject: Optional[str],
        body: str
    ) -> Optional[TemplateTranslation]:
        """
        Add or update translation for a template
        
        Args:
            template_id: Template identifier
            language_code: Language code (e.g., 'es', 'fr')
            subject: Translated subject
            body: Translated body
            
        Returns:
            Created or updated translation
        """
        template = self.get_template(template_id)
        if not template:
            logger.warning(f"Template '{template_id}' not found for translation")
            return None
        
        # Check if translation exists
        existing = self.db.query(TemplateTranslation).filter(
            and_(
                TemplateTranslation.template_id == template.id,
                TemplateTranslation.language_code == language_code
            )
        ).first()
        
        if existing:
            # Update existing translation
            logger.info(f"Updating existing translation '{language_code}' for template '{template_id}'")
            existing.subject = subject
            existing.body = body
            existing.is_active = True
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # Create new translation
        logger.info(f"Creating new translation '{language_code}' for template '{template_id}'")
        translation = TemplateTranslation(
            template_id=template.id,
            language_code=language_code,
            subject=subject,
            body=body
        )
        self.db.add(translation)
        self.db.commit()
        self.db.refresh(translation)
        
        return translation
    
    def get_template_versions(self, template_id: str) -> List[TemplateVersion]:
        """
        Get all versions of a template
        
        Args:
            template_id: Template identifier
            
        Returns:
            List of template versions, ordered by creation date (newest first)
        """
        template = self.get_template(template_id)
        if not template:
            return []
        
        versions = self.db.query(TemplateVersion).filter(
            TemplateVersion.template_id == template.id
        ).order_by(TemplateVersion.created_at.desc()).all()
        
        logger.debug(f"Retrieved {len(versions)} versions for template '{template_id}'")
        return versions
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get template statistics
        
        Returns:
            Dictionary with various statistics
        """
        total_templates = self.db.query(Template).filter(Template.is_active == True).count()
        total_versions = self.db.query(TemplateVersion).count()
        total_translations = self.db.query(TemplateTranslation).filter(
            TemplateTranslation.is_active == True
        ).count()
        
        # Count by type
        type_counts = {}
        for template_type in ['email', 'push', 'sms']:
            count = self.db.query(Template).filter(
                and_(
                    Template.type == template_type,
                    Template.is_active == True
                )
            ).count()
            type_counts[template_type] = count
        
        return {
            "total_templates": total_templates,
            "total_versions": total_versions,
            "total_translations": total_translations,
            "templates_by_type": type_counts
        }