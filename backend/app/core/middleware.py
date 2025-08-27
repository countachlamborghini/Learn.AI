from fastapi import Request, Response
import time
import logging
from typing import Callable
import json

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {scope['method']} {scope['path']}")
        
        # Process request
        await self.app(scope, receive, send)
        
        # Log response time
        process_time = time.time() - start_time
        logger.info(f"Response time: {process_time:.4f}s")

class RateLimitMiddleware:
    def __init__(self, app, rate_limit: int = 60):
        self.app = app
        self.rate_limit = rate_limit
        self.requests = {}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get client IP
        client_ip = scope.get("client", ("", ""))[0]
        
        # Check rate limit
        current_time = time.time()
        if client_ip in self.requests:
            # Clean old requests
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60
            ]
            
            if len(self.requests[client_ip]) >= self.rate_limit:
                # Rate limit exceeded
                response = Response(
                    content=json.dumps({"detail": "Rate limit exceeded"}),
                    status_code=429,
                    media_type="application/json"
                )
                await response(scope, receive, send)
                return
        
        # Add current request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)
        
        await self.app(scope, receive, send)