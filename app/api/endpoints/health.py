from datetime import datetime
from fastapi import APIRouter, Depends
import boto3
import logging
from app.api.dependencies import get_bedrock_client

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", summary="Health check endpoint")
async def health_check():
    """
    Simple health check endpoint that returns the service status and current time.
    This endpoint is publicly accessible without authentication.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "bedrock-api-bridge"
    }

@router.get("/health/bedrock", summary="AWS Bedrock service health check")
async def bedrock_health_check(client = Depends(get_bedrock_client)):
    """
    Checks the connection to AWS Bedrock service.
    This endpoint is publicly accessible without authentication.
    """
    try:
        # Minimal API call to check Bedrock service connectivity
        # Listing models is a lightweight operation that verifies our credentials and connectivity
        response = client.list_foundation_models(maxResults=1)
        return {
            "status": "connected", 
            "timestamp": datetime.utcnow().isoformat(),
            "service": "aws-bedrock"
        }
    except Exception as e:
        logger.error(f"AWS Bedrock health check failed: {str(e)}")
        return {
            "status": "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "aws-bedrock",
            "error": str(e)
        }