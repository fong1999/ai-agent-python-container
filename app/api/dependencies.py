import boto3
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# API Key security scheme
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

# AWS Bedrock client dependency
def get_bedrock_client():
    """
    Dependency for getting an AWS Bedrock client
    """
    try:
        return boto3.client('bedrock-runtime', region_name=settings.AWS_REGION)
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock client: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Failed to connect to AWS Bedrock service"
        )

# API Key validation dependency
async def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Dependency for verifying API key
    """
    if not settings.API_KEYS:
        # If no API keys are configured, fail securely
        logger.error("No API keys configured but authentication is required")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Server authentication misconfiguration"
        )
        
    if api_key not in settings.API_KEYS:
        logger.warning(f"Invalid API key attempt: {api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    return api_key

# Common security dependencies
security_dependencies = [Depends(verify_api_key)]