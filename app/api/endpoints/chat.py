import logging
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from typing import List

from app.api.dependencies import get_bedrock_client, security_dependencies
from app.models.chat import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChoice, ChatCompletionUsage, Message
from app.services.bedrock import BedrockService
from app.services.usage_tracking import track_usage
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/v1/chat/completions", 
    response_model=ChatCompletionResponse,
    dependencies=security_dependencies,
    summary="Create a chat completion"
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    background_tasks: BackgroundTasks,
    bedrock_client = Depends(get_bedrock_client),
    http_request: Request = None,
):
    """
    Create a completion for a chat conversation.
    
    This endpoint is compatible with the OpenAI API format for easier frontend integration.
    """
    try:
        bedrock_service = BedrockService(bedrock_client)
        
        # Handle streaming responses
        if request.stream:
            async def generate_stream():
                try:
                    async for chunk in bedrock_service.generate_completion_stream(
                        model_id=request.model,
                        messages=request.messages,
                        max_tokens=request.max_tokens,
                        temperature=request.temperature
                    ):
                        # Convert to SSE format
                        yield f"data: {chunk.model_dump_json(exclude_none=True)}\n\n"
                    
                    # End of stream marker
                    yield "data: [DONE]\n\n"
                    
                    # Track usage in background after completion
                    background_tasks.add_task(
                        track_usage,
                        model=request.model,
                        tokens=1000,  # Estimate for streaming
                        user_id=request.user_id,
                        http_request=http_request
                    )
                except Exception as e:
                    logger.error(f"Streaming error: {str(e)}")
                    error_data = {"error": {"message": str(e), "type": "server_error"}}
                    yield f"data: {json.dumps(error_data)}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream"
            )
        
        # Handle non-streaming responses
        else:
            response = await bedrock_service.generate_completion(
                model_id=request.model,
                messages=request.messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # Track usage in background
            background_tasks.add_task(
                track_usage,
                model=request.model,
                tokens=response.get("usage", {}).get("total_tokens", 0),
                user_id=request.user_id,
                http_request=http_request
            )
            
            # Format response to match OpenAI-like structure
            completion_response = ChatCompletionResponse(
                model=request.model,
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=Message(
                            role="assistant",
                            content=response.get("completion", "")
                        ),
                        finish_reason="stop"
                    )
                ],
                usage=ChatCompletionUsage(
                    prompt_tokens=response.get("usage", {}).get("prompt_tokens", 0),
                    completion_tokens=response.get("usage", {}).get("completion_tokens", 0),
                    total_tokens=response.get("usage", {}).get("total_tokens", 0)
                )
            )
            
            return completion_response
            
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))