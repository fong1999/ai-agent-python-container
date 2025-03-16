import json
import boto3
import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator

from app.models.chat import Message, ChatCompletionChunk, ChatCompletionChunkChoice, ChatCompletionChunkDelta
from app.core.config import settings

logger = logging.getLogger(__name__)

class BedrockService:
    """Service for interacting with AWS Bedrock models"""
    
    def __init__(self, client=None):
        """Initialize with an optional boto3 bedrock-runtime client"""
        self.client = client or boto3.client('bedrock-runtime', region_name=settings.AWS_REGION)
    
    def _create_request_body(self, model_id: str, messages: List[Message], max_tokens: Optional[int] = None, 
                           temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Create the appropriate request body for the model
        """
        # Default values if not provided
        max_tokens = max_tokens or settings.DEFAULT_MAX_TOKENS
        temperature = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
        
        # Convert chat format to model-specific format
        if "claude" in model_id.lower():
            return self._create_anthropic_body(messages, max_tokens, temperature)
        elif "llama" in model_id.lower():
            return self._create_meta_body(messages, max_tokens, temperature)
        else:
            logger.warning(f"Unknown model format for {model_id}, defaulting to Claude format")
            return self._create_anthropic_body(messages, max_tokens, temperature)
    
    def _create_anthropic_body(self, messages: List[Message], max_tokens: int, temperature: float) -> Dict[str, Any]:
        """
        Create request body for Anthropic Claude models
        """
        # Start with system prompt if present
        anthropic_prompt = ""
        system_messages = [msg for msg in messages if msg.role == "system"]
        if system_messages:
            anthropic_prompt = system_messages[0].content + "\n\n"
        
        # Add conversation messages
        for msg in messages:
            if msg.role == "system":
                continue  # Already handled above
            elif msg.role == "user":
                anthropic_prompt += f"Human: {msg.content}\n\n"
            elif msg.role == "assistant":
                anthropic_prompt += f"Assistant: {msg.content}\n\n"
        
        # Add final assistant prompt
        anthropic_prompt += "Assistant:"
        
        return {
            "prompt": anthropic_prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
            "anthropic_version": "bedrock-2023-05-31"
        }
    
    def _create_meta_body(self, messages: List[Message], max_tokens: int, temperature: float) -> Dict[str, Any]:
        """
        Create request body for Meta Llama models
        """
        # Llama uses a different format
        prompt = ""
        for msg in messages:
            if msg.role == "system":
                prompt += f"<system>\n{msg.content}\n</system>\n"
            elif msg.role == "user":
                prompt += f"<human>\n{msg.content}\n</human>\n"
            elif msg.role == "assistant":
                prompt += f"<assistant>\n{msg.content}\n</assistant>\n"
        
        # Final assistant turn
        prompt += "<assistant>\n"
        
        return {
            "prompt": prompt,
            "max_gen_len": max_tokens,
            "temperature": temperature
        }
    
    async def generate_completion(self, model_id: str, messages: List[Message], max_tokens: Optional[int] = None,
                               temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate a completion using AWS Bedrock
        """
        request_body = self._create_request_body(model_id, messages, max_tokens, temperature)
        
        try:
            logger.debug(f"Calling Bedrock model {model_id}")
            response = self.client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            logger.debug(f"Received response from Bedrock")
            
            # Extract the completion based on model
            if "claude" in model_id.lower():
                completion = response_body.get("completion", "").strip()
            elif "llama" in model_id.lower():
                completion = response_body.get("generation", "").strip()
            else:
                completion = response_body.get("completion", response_body.get("generation", "")).strip()
            
            # Estimate token usage - this is approximate
            prompt_tokens = len(request_body.get("prompt", "")) // 4
            completion_tokens = len(completion) // 4
            
            return {
                "completion": completion,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Bedrock completion: {str(e)}")
            raise
    
    async def generate_completion_stream(self, model_id: str, messages: List[Message], 
                                       max_tokens: Optional[int] = None,
                                       temperature: Optional[float] = None,
                                       ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """
        Generate a streaming completion
        Note: AWS Bedrock doesn't natively support streaming for all models.
        This implementation simulates streaming by breaking a complete response into chunks.
        """
        try:
            # Get the full completion first
            response = await self.generate_completion(model_id, messages, max_tokens, temperature)
            completion = response.get("completion", "")
            
            # Break into chunks and yield
            chunk_size = 20  # Simulating stream with 20-char chunks
            for i in range(0, len(completion), chunk_size):
                chunk = completion[i:i+chunk_size]
                
                # Create SSE-compatible chunk
                yield ChatCompletionChunk(
                    model=model_id,
                    choices=[
                        ChatCompletionChunkChoice(
                            index=0,
                            delta=ChatCompletionChunkDelta(content=chunk),
                            finish_reason=None if i + chunk_size < len(completion) else "stop"
                        )
                    ]
                )
                
                # Small delay to simulate streaming
                await asyncio.sleep(0.05)
            
        except Exception as e:
            logger.error(f"Error in Bedrock streaming: {str(e)}")
            raise