"""
Template rendering utility using Jinja2
"""

from jinja2 import Environment, BaseLoader, TemplateError, TemplateSyntaxError
import re
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Handles template variable substitution using Jinja2"""
    
    def __init__(self):
        """Initialize Jinja2 environment"""
        self.env = Environment(
            loader=BaseLoader(),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render(self, template_string: str, data: Dict[str, Any]) -> str:
        """
        Render a template with provided data
        
        Args:
            template_string: Template with {{variable}} placeholders
            data: Dictionary of variable values
            
        Returns:
            Rendered string
            
        Raises:
            ValueError: If template rendering fails
        """
        try:
            template = self.env.from_string(template_string)
            rendered = template.render(**data)
            logger.debug(f"Template rendered successfully with {len(data)} variables")
            return rendered
        except TemplateSyntaxError as e:
            error_msg = f"Template syntax error at line {e.lineno}: {e.message}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except TemplateError as e:
            error_msg = f"Template rendering error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during template rendering: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def extract_variables(self, template_string: str) -> List[str]:
        """
        Extract variable names from template
        
        Args:
            template_string: Template with {{variable}} placeholders
            
        Returns:
            List of unique variable names
        """
        try:
            # Match Jinja2 variable syntax: {{ variable }}
            pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
            variables = re.findall(pattern, template_string)
            unique_vars = list(set(variables))
            logger.debug(f"Extracted {len(unique_vars)} unique variables from template")
            return unique_vars
        except Exception as e:
            logger.error(f"Failed to extract variables: {str(e)}")
            return []
    
    def validate_variables(
        self, 
        template_string: str, 
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check if all required variables are provided
        
        Args:
            template_string: Template string
            data: Provided variable data
            
        Returns:
            Tuple of (is_valid, missing_variables)
        """
        required_vars = self.extract_variables(template_string)
        provided_vars = set(data.keys())
        missing_vars = [v for v in required_vars if v not in provided_vars]
        
        is_valid = len(missing_vars) == 0
        
        if not is_valid:
            logger.warning(f"Missing variables: {missing_vars}")
        
        return is_valid, missing_vars
    
    def preview_render(
        self, 
        template_string: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Preview template rendering with validation
        
        Args:
            template_string: Template string
            data: Variable data
            
        Returns:
            Dictionary with rendered content and metadata
        """
        is_valid, missing = self.validate_variables(template_string, data)
        
        if not is_valid:
            return {
                "success": False,
                "error": f"Missing required variables: {', '.join(missing)}",
                "missing_variables": missing
            }
        
        try:
            rendered = self.render(template_string, data)
            return {
                "success": True,
                "rendered": rendered,
                "variables_used": self.extract_variables(template_string)
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }