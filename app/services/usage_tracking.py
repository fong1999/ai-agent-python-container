import logging
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request

from app.core.config import settings

logger = logging.getLogger(__name__)

async def track_usage(
    model: str,
    tokens: int,
    user_id: Optional[str] = None,
    http_request: Optional[Request] = None
):
    """
    Track API usage for billing, monitoring, and rate limiting purposes.
    
    In a production system, this would typically write to a database or send to a monitoring service.
    For this example, we'll just log the usage, but the structure is in place to extend.
    
    Args:
        model: The model ID used
        tokens: Number of tokens used
        user_id: Optional user identifier
        http_request: Optional request object for extracting additional metadata
    """
    if not settings.TRACK_USAGE:
        return
    
    # Extract request metadata if available
    request_metadata = {}
    if http_request:
        client_host = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("User-Agent", "unknown")
        request_id = http_request.headers.get("X-Request-ID", "unknown")
        
        request_metadata = {
            "client_ip": client_host,
            "user_agent": user_agent,
            "request_id": request_id,
            "path": str(http_request.url.path),
            "method": http_request.method,
        }
    
    # Create usage record
    usage_record = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": model,
        "tokens": tokens,
        "user_id": user_id or "anonymous",
        "cost_estimate": estimate_cost(model, tokens),
        "request": request_metadata
    }
    
    # In a real implementation, you would store this in a database or send to a monitoring system
    # For this example, we'll just log it
    logger.info(f"Usage tracked: {json.dumps(usage_record)}")
    
    # Example of extending this:
    # await store_usage_in_database(usage_record)
    # await send_to_monitoring_service(usage_record)
    # await check_rate_limits(user_id, tokens)
    
    return usage_record

def estimate_cost(model: str, tokens: int) -> float:
    """
    Estimate the cost of the API call based on model and tokens used.
    This is a simplified example - real pricing would come from AWS.
    
    Args:
        model: The model ID
        tokens: Number of tokens used
        
    Returns:
        Estimated cost in USD
    """
    # Example pricing rates per 1000 tokens (these should be updated with actual AWS rates)
    model_rates = {
        "anthropic.claude-v2": 0.008,
        "anthropic.claude-instant-v1": 0.0004,
        "anthropic.claude-3-sonnet-20240229-v1:0": 0.003,
        "anthropic.claude-3-haiku-20240307-v1:0": 0.00025,
        "meta.llama2-13b-chat-v1": 0.00075
    }
    
    # Default rate if model not found
    default_rate = 0.005
    
    # Get rate for this model or use default
    rate_per_1k = model_rates.get(model, default_rate)
    
    # Calculate and return cost
    return (tokens / 1000) * rate_per_1k