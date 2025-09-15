"""
Response Utilities
Standardized response formatting for API endpoints
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from flask import jsonify, request

logger = logging.getLogger(__name__)

def success_response(
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    Create standardized success response
    
    Args:
        message: Success message
        data: Response data
        status_code: HTTP status code
        metadata: Additional metadata
        
    Returns:
        Tuple of (response, status_code)
    """
    
    response_data = {
        'success': True,
        'message': message,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if data is not None:
        response_data['data'] = data
    
    if metadata:
        response_data['metadata'] = metadata
    
    # Add request info for debugging
    if request:
        response_data['request_id'] = getattr(request, 'id', None)
    
    logger.info(f"Success response: {message}")
    
    return jsonify(response_data), status_code

def error_response(
    message: str,
    details: Optional[Union[str, Dict, List]] = None,
    status_code: int = 400,
    error_code: Optional[str] = None
) -> tuple:
    """
    Create standardized error response
    
    Args:
        message: Error message
        details: Error details
        status_code: HTTP status code
        error_code: Custom error code
        
    Returns:
        Tuple of (response, status_code)
    """
    
    response_data = {
        'success': False,
        'error': {
            'message': message,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    }
    
    if details is not None:
        response_data['error']['details'] = details
    
    if error_code:
        response_data['error']['code'] = error_code
    
    # Add request info for debugging
    if request:
        response_data['error']['request_id'] = getattr(request, 'id', None)
        response_data['error']['endpoint'] = request.endpoint
        response_data['error']['method'] = request.method
    
    logger.warning(f"Error response: {message} (Status: {status_code})")
    
    return jsonify(response_data), status_code

def validation_error_response(
    validation_errors: Union[Dict, List, str],
    message: str = "Validation failed"
) -> tuple:
    """
    Create response for validation errors
    
    Args:
        validation_errors: Validation error details
        message: Error message
        
    Returns:
        Tuple of (response, status_code)
    """
    
    return error_response(
        message=message,
        details=validation_errors,
        status_code=400,
        error_code='VALIDATION_ERROR'
    )

def not_found_response(
    resource: str = "Resource",
    resource_id: Optional[str] = None
) -> tuple:
    """
    Create standardized 404 response
    
    Args:
        resource: Resource type that wasn't found
        resource_id: ID of the resource
        
    Returns:
        Tuple of (response, status_code)
    """
    
    message = f"{resource} not found"
    if resource_id:
        message += f" (ID: {resource_id})"
    
    return error_response(
        message=message,
        status_code=404,
        error_code='NOT_FOUND'
    )

def unauthorized_response(
    message: str = "Authentication required"
) -> tuple:
    """
    Create standardized 401 response
    
    Args:
        message: Unauthorized message
        
    Returns:
        Tuple of (response, status_code)
    """
    
    return error_response(
        message=message,
        status_code=401,
        error_code='UNAUTHORIZED'
    )

def forbidden_response(
    message: str = "Access denied"
) -> tuple:
    """
    Create standardized 403 response
    
    Args:
        message: Forbidden message
        
    Returns:
        Tuple of (response, status_code)
    """
    
    return error_response(
        message=message,
        status_code=403,
        error_code='FORBIDDEN'
    )

def rate_limit_response(
    message: str = "Rate limit exceeded",
    retry_after: Optional[int] = None
) -> tuple:
    """
    Create standardized 429 response
    
    Args:
        message: Rate limit message
        retry_after: Seconds to wait before retry
        
    Returns:
        Tuple of (response, status_code)
    """
    
    details = {}
    if retry_after:
        details['retry_after_seconds'] = retry_after
    
    response = error_response(
        message=message,
        details=details if details else None,
        status_code=429,
        error_code='RATE_LIMIT_EXCEEDED'
    )
    
    # Add Retry-After header if specified
    if retry_after:
        response[0].headers['Retry-After'] = str(retry_after)
    
    return response

def server_error_response(
    message: str = "Internal server error",
    error_id: Optional[str] = None
) -> tuple:
    """
    Create standardized 500 response
    
    Args:
        message: Error message
        error_id: Unique error identifier for tracking
        
    Returns:
        Tuple of (response, status_code)
    """
    
    details = {}
    if error_id:
        details['error_id'] = error_id
        details['support_message'] = f"If this problem persists, contact support with error ID: {error_id}"
    
    return error_response(
        message=message,
        details=details if details else None,
        status_code=500,
        error_code='INTERNAL_ERROR'
    )

def service_unavailable_response(
    service_name: str = "Service",
    message: Optional[str] = None
) -> tuple:
    """
    Create standardized 503 response
    
    Args:
        service_name: Name of unavailable service
        message: Custom message
        
    Returns:
        Tuple of (response, status_code)
    """
    
    if not message:
        message = f"{service_name} temporarily unavailable"
    
    return error_response(
        message=message,
        status_code=503,
        error_code='SERVICE_UNAVAILABLE'
    )

def paginated_response(
    items: List[Any],
    page: int,
    per_page: int,
    total_items: int,
    message: str = "Data retrieved successfully"
) -> tuple:
    """
    Create paginated response
    
    Args:
        items: List of items for current page
        page: Current page number
        per_page: Items per page
        total_items: Total number of items
        message: Success message
        
    Returns:
        Tuple of (response, status_code)
    """
    
    total_pages = (total_items + per_page - 1) // per_page
    
            pagination_data = {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'next_page': page + 1 if page < total_pages else None,
            'prev_page': page - 1 if page > 1 else None
        }
    }
    
    return success_response(
        message=message,
        data=pagination_data,
        status_code=200
    )

def batch_response(
    results: List[Dict[str, Any]],
    message: str = "Batch operation completed"
) -> tuple:
    """
    Create response for batch operations
    
    Args:
        results: List of operation results
        message: Success message
        
    Returns:
        Tuple of (response, status_code)
    """
    
    successful = sum(1 for r in results if r.get('success', False))
    failed = len(results) - successful
    
    batch_data = {
        'results': results,
        'summary': {
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(results)) * 100 if results else 0
        }
    }
    
    # Determine overall status
    if failed == 0:
        status_code = 200
        final_message = f"{message} - All operations successful"
    elif successful == 0:
        status_code = 400
        final_message = f"{message} - All operations failed"
    else:
        status_code = 207  # Multi-Status
        final_message = f"{message} - {successful} successful, {failed} failed"
    
    return success_response(
        message=final_message,
        data=batch_data,
        status_code=status_code
    )

def async_job_response(
    job_id: str,
    status: str = "processing",
    message: str = "Job created successfully"
) -> tuple:
    """
    Create response for asynchronous job creation
    
    Args:
        job_id: Unique job identifier
        status: Job status
        message: Success message
        
    Returns:
        Tuple of (response, status_code)
    """
    
    job_data = {
        'job_id': job_id,
        'status': status,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'status_url': f"/api/v1/jobs/{job_id}/status",
        'result_url': f"/api/v1/jobs/{job_id}/result"
    }
    
    return success_response(
        message=message,
        data=job_data,
        status_code=202  # Accepted
    )

def job_status_response(
    job_id: str,
    status: str,
    progress: Optional[int] = None,
    result: Optional[Any] = None,
    error: Optional[str] = None
) -> tuple:
    """
    Create response for job status check
    
    Args:
        job_id: Job identifier
        status: Current job status
        progress: Progress percentage (0-100)
        result: Job result (if completed)
        error: Error message (if failed)
        
    Returns:
        Tuple of (response, status_code)
    """
    
    job_data = {
        'job_id': job_id,
        'status': status,
        'checked_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    if progress is not None:
        job_data['progress'] = progress
    
    if status == 'completed' and result is not None:
        job_data['result'] = result
        message = "Job completed successfully"
        status_code = 200
    elif status == 'failed' and error:
        job_data['error'] = error
        message = "Job failed"
        status_code = 200  # Still 200 for successful status check
    elif status == 'processing':
        message = "Job is still processing"
        status_code = 200
        if progress is not None:
            job_data['estimated_completion'] = "unknown"
    else:
        message = f"Job status: {status}"
        status_code = 200
    
    return success_response(
        message=message,
        data=job_data,
        status_code=status_code
    )

def health_check_response(
    status: str = "healthy",
    checks: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    Create health check response
    
    Args:
        status: Overall health status
        checks: Individual health checks
        
    Returns:
        Tuple of (response, status_code)
    """
    
    health_data = {
        'status': status,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0'
    }
    
    if checks:
        health_data['checks'] = checks
    
    # Determine status code based on health
    if status == 'healthy':
        status_code = 200
        message = "Service is healthy"
    elif status == 'degraded':
        status_code = 200
        message = "Service is degraded but operational"
    else:
        status_code = 503
        message = "Service is unhealthy"
    
    return success_response(
        message=message,
        data=health_data,
        status_code=status_code
    )

def api_info_response(
    name: str,
    version: str,
    description: str,
    endpoints: Optional[Dict[str, str]] = None
) -> tuple:
    """
    Create API information response
    
    Args:
        name: API name
        version: API version
        description: API description
        endpoints: Available endpoints
        
    Returns:
        Tuple of (response, status_code)
    """
    
    api_data = {
        'name': name,
        'version': version,
        'description': description,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if endpoints:
        api_data['endpoints'] = endpoints
    
    return success_response(
        message="API information",
        data=api_data,
        status_code=200
    )

def metrics_response(
    metrics: Dict[str, Any],
    time_range: Optional[str] = None
) -> tuple:
    """
    Create metrics response
    
    Args:
        metrics: Metrics data
        time_range: Time range for metrics
        
    Returns:
        Tuple of (response, status_code)
    """
    
    metrics_data = {
        'metrics': metrics,
        'collected_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    if time_range:
        metrics_data['time_range'] = time_range
    
    return success_response(
        message="Metrics retrieved successfully",
        data=metrics_data,
        status_code=200
    )

def cache_response(
    data: Any,
    cache_info: Dict[str, Any],
    message: str = "Data retrieved successfully"
) -> tuple:
    """
    Create response with cache information
    
    Args:
        data: Response data
        cache_info: Cache metadata
        message: Success message
        
    Returns:
        Tuple of (response, status_code)
    """
    
    metadata = {
        'cache': cache_info
    }
    
    response = success_response(
        message=message,
        data=data,
        metadata=metadata,
        status_code=200
    )
    
    # Add cache headers
    if 'expires_at' in cache_info:
        response[0].headers['Cache-Control'] = f"max-age={cache_info.get('max_age', 3600)}"
        response[0].headers['Expires'] = cache_info['expires_at']
    
    if cache_info.get('etag'):
        response[0].headers['ETag'] = cache_info['etag']
    
    return response

def file_download_response(
    file_data: bytes,
    filename: str,
    mime_type: str = 'application/octet-stream'
) -> tuple:
    """
    Create file download response
    
    Args:
        file_data: File content as bytes
        filename: Name for downloaded file
        mime_type: MIME type of file
        
    Returns:
        Tuple of (response, status_code)
    """
    
    from flask import Response
    
    response = Response(
        file_data,
        mimetype=mime_type,
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(len(file_data))
        }
    )
    
    return response, 200

def redirect_response(
    url: str,
    permanent: bool = False,
    message: Optional[str] = None
) -> tuple:
    """
    Create redirect response
    
    Args:
        url: Redirect URL
        permanent: Whether redirect is permanent
        message: Optional message
        
    Returns:
        Tuple of (response, status_code)
    """
    
    status_code = 301 if permanent else 302
    
    response_data = {
        'success': True,
        'redirect_url': url,
        'permanent': permanent
    }
    
    if message:
        response_data['message'] = message
    
    response = jsonify(response_data)
    response.headers['Location'] = url
    
    return response, status_code
