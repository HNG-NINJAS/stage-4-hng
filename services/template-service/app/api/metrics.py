"""
Metrics tracking for template operations
"""

import logging
from typing import Dict
from collections import defaultdict
from fastapi import APIRouter, status

from app.utils.response import success_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])

# In-memory metrics storage (for production, use Prometheus or similar)
operation_metrics: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
render_times: Dict[str, list] = defaultdict(list)


def track_operation(operation: str, status: str) -> None:
    """
    Track template operations for monitoring
    
    Args:
        operation: Operation type (create, update, delete, render, etc.)
        status: Operation status (success, error, not_found)
    """
    operation_metrics[operation][status] += 1
    logger.debug(f"Tracked operation: {operation} - {status}")


def track_request(method: str, endpoint: str, status_code: int) -> None:
    """
    Track HTTP requests for monitoring
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        endpoint: Request endpoint path
        status_code: HTTP response status code
    """
    key = f"{method}:{endpoint}"
    operation_metrics["requests"][key] += 1
    operation_metrics["status_codes"][str(status_code)] += 1
    logger.debug(f"Tracked request: {method} {endpoint} - {status_code}")


def track_render_time(template_id: str, duration: float) -> None:
    """
    Track template render time for performance monitoring
    
    Args:
        template_id: Template identifier
        duration: Render duration in seconds
    """
    render_times[template_id].append(duration)
    # Keep only last 100 render times per template
    if len(render_times[template_id]) > 100:
        render_times[template_id] = render_times[template_id][-100:]
    logger.debug(f"Tracked render time for {template_id}: {duration:.3f}s")


def get_metrics() -> Dict:
    """
    Get current metrics snapshot
    
    Returns:
        Dictionary containing operation counts and render statistics
    """
    metrics = {
        "operations": dict(operation_metrics),
        "render_stats": {}
    }
    
    # Calculate render time statistics
    for template_id, times in render_times.items():
        if times:
            metrics["render_stats"][template_id] = {
                "count": len(times),
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times)
            }
    
    return metrics


def reset_metrics() -> None:
    """Reset all metrics (useful for testing)"""
    operation_metrics.clear()
    render_times.clear()
    logger.info("Metrics reset")


@router.get("", status_code=status.HTTP_200_OK)
def get_metrics_endpoint():
    """
    Get service metrics
    
    Returns operation counts, request statistics, and render performance data
    """
    metrics_data = get_metrics()
    return success_response(
        message="Metrics retrieved successfully",
        data=metrics_data
    )
