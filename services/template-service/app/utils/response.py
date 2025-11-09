"""
Standardized API response helper
"""

from typing import Optional, Any
from app.schemas import ApiResponse, PaginationMeta


def create_response(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    error: Optional[str] = None,
    total: int = 0,
    limit: int = 10,
    page: int = 1
) -> dict:
    """
    Create standardized API response
    
    Args:
        success: Whether the request was successful
        message: Human-readable message
        data: Response data (optional)
        error: Error code if failed (optional)
        total: Total number of items
        limit: Items per page
        page: Current page number
        
    Returns:
        Standardized response dictionary
    """
    # Calculate pagination
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    
    meta = PaginationMeta(
        total=total,
        limit=limit,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )
    
    response = ApiResponse(
        success=success,
        data=data,
        error=error,
        message=message,
        meta=meta
    )
    
    return response.model_dump()


def success_response(
    message: str, 
    data: Any = None, 
    total: int = 0,
    limit: int = 10,
    page: int = 1
) -> dict:
    """
    Shortcut for success responses
    
    Args:
        message: Success message
        data: Response data
        total: Total items
        limit: Items per page
        page: Current page
        
    Returns:
        Success response dictionary
    """
    # If data is a single item, set total to 1
    if data is not None and not isinstance(data, list) and total == 0:
        total = 1
    
    return create_response(
        success=True,
        message=message,
        data=data,
        total=total,
        limit=limit,
        page=page
    )


def error_response(
    message: str, 
    error: str,
    data: Any = None,
    total: int = 0,
    limit: int = 10,
    page: int = 1
) -> dict:
    """
    Shortcut for error responses
    
    Args:
        message: Error message
        error: Error code
        data: Optional error data
        total: Total items
        limit: Items per page
        page: Current page
        
    Returns:
        Error response dictionary
    """
    return create_response(
        success=False,
        message=message,
        error=error,
        data=data,
        total=total,
        limit=limit,
        page=page
    )