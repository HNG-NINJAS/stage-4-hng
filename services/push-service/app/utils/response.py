"""Standard API responses"""

from typing import Optional, Any


def create_response(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> dict:
    """Create standardized response"""
    return {
        "success": success,
        "data": data,
        "error": error,
        "message": message,
        "meta": {
            "total": 1 if data else 0,
            "limit": 10,
            "page": 1,
            "total_pages": 1 if data else 0,
            "has_next": False,
            "has_previous": False
        }
    }


def success_response(message: str, data: Any = None) -> dict:
    """Success response"""
    return create_response(success=True, message=message, data=data)


def error_response(message: str, error: str) -> dict:
    """Error response"""
    return create_response(success=False, message=message, error=error)