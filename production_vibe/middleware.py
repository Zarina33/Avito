"""
Production Middleware
Handles validation, error handling, rate limiting, and request tracing
"""
import uuid
import time
import functools
from typing import Dict, Callable
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock

from flask import request, jsonify, g
from werkzeug.exceptions import HTTPException
import logging

from config import config

logger = logging.getLogger(__name__)


# ===============================
# Request ID Middleware
# ===============================

class RequestIDMiddleware:
    """Adds unique request ID to each request for tracing"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    @staticmethod
    def before_request():
        """Generate request ID before handling request"""
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.start_time = time.time()
    
    @staticmethod
    def after_request(response):
        """Add request ID to response headers"""
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response


# ===============================
# Rate Limiting
# ===============================

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, client_id: str, max_per_minute: int, max_per_hour: int) -> tuple[bool, str]:
        """
        Check if request is allowed based on rate limits
        Returns (is_allowed, error_message)
        """
        with self.lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            
            # Clean old requests
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > hour_ago
            ]
            
            recent_requests = self.requests[client_id]
            
            # Check minute limit
            minute_requests = [t for t in recent_requests if t > minute_ago]
            if len(minute_requests) >= max_per_minute:
                return False, f"Rate limit exceeded: {max_per_minute} requests per minute"
            
            # Check hour limit
            if len(recent_requests) >= max_per_hour:
                return False, f"Rate limit exceeded: {max_per_hour} requests per hour"
            
            # Add current request
            self.requests[client_id].append(now)
            return True, ""
    
    def get_stats(self, client_id: str) -> dict:
        """Get rate limit stats for a client"""
        with self.lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            
            recent = self.requests.get(client_id, [])
            minute_count = len([t for t in recent if t > minute_ago])
            hour_count = len([t for t in recent if t > hour_ago])
            
            return {
                "requests_last_minute": minute_count,
                "requests_last_hour": hour_count,
                "limit_per_minute": config.security.rate_limit_per_minute,
                "limit_per_hour": config.security.rate_limit_per_hour,
            }


rate_limiter = RateLimiter()


def rate_limit_required(f: Callable) -> Callable:
    """Decorator to enforce rate limiting"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Use IP address as client identifier
        client_id = request.remote_addr or "unknown"
        
        allowed, error_msg = rate_limiter.is_allowed(
            client_id,
            config.security.rate_limit_per_minute,
            config.security.rate_limit_per_hour
        )
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_id}")
            return jsonify({
                "error": "rate_limit_exceeded",
                "message": error_msg,
                "request_id": getattr(g, 'request_id', None)
            }), 429
        
        return f(*args, **kwargs)
    return decorated_function


# ===============================
# Error Handling
# ===============================

class APIError(Exception):
    """Base API error class"""
    status_code = 500
    
    def __init__(self, message: str, status_code: int = None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.__class__.__name__
        rv['message'] = self.message
        rv['request_id'] = getattr(g, 'request_id', None)
        return rv


class ValidationError(APIError):
    """Validation error"""
    status_code = 400


class ModelError(APIError):
    """Model inference error"""
    status_code = 500


def setup_error_handlers(app):
    """Setup global error handlers"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        logger.error(f"API Error: {error.message}", extra={'request_id': getattr(g, 'request_id', 'N/A')})
        return response
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = jsonify({
            'error': error.name,
            'message': error.description,
            'request_id': getattr(g, 'request_id', None)
        })
        response.status_code = error.code
        return response
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Unexpected error", extra={'request_id': getattr(g, 'request_id', 'N/A')})
        response = jsonify({
            'error': 'internal_server_error',
            'message': 'An unexpected error occurred',
            'request_id': getattr(g, 'request_id', None)
        })
        response.status_code = 500
        return response


# ===============================
# Input Validation
# ===============================

def validate_prompt(prompt: str, max_length: int = None) -> str:
    """Validate text prompt"""
    if not prompt:
        raise ValidationError("Prompt cannot be empty")
    
    if not isinstance(prompt, str):
        raise ValidationError("Prompt must be a string")
    
    prompt = prompt.strip()
    
    max_len = max_length or config.security.max_prompt_length
    if len(prompt) > max_len:
        raise ValidationError(f"Prompt too long. Maximum length: {max_len} characters")
    
    return prompt


def validate_image_file(file) -> None:
    """Validate uploaded image file"""
    if not file:
        raise ValidationError("No image file provided")
    
    if not file.filename:
        raise ValidationError("Invalid file upload")
    
    # Check file extension
    import os
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in config.security.allowed_image_extensions:
        raise ValidationError(
            f"Invalid file type. Allowed: {', '.join(config.security.allowed_image_extensions)}"
        )
    
    # Check file size (already handled by Flask MAX_CONTENT_LENGTH, but double check)
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset
    
    max_size = 16 * 1024 * 1024  # 16MB
    if size > max_size:
        raise ValidationError(f"File too large. Maximum size: {max_size / (1024*1024):.0f}MB")
    
    if size == 0:
        raise ValidationError("File is empty")


# ===============================
# Request Context Logger
# ===============================

class RequestContextFilter(logging.Filter):
    """Add request context to log records"""
    
    def filter(self, record):
        record.request_id = getattr(g, 'request_id', 'N/A')
        return True

