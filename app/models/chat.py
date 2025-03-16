from typing import List, Optional, Union, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

class Message(BaseModel):
    """A single message in a chat conversation"""
    role: Literal["system", "user", "assistant"] = Field(
        ..., description="The role of the message sender"
    )
    content: str = Field(..., description="The content of the message")

class ChatCompletionRequest(BaseModel):
    """Request body for chat completion endpoint"""
    model: str = Field(..., description="The ID of the model to use")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(None, description="Sampling temperature")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    user_id: Optional[str] = Field(None, description="Optional user identifier for tracking")
    
    @validator("temperature")
    def validate_temperature(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError("Temperature must be between 0 and 1")
        return v

class ChatCompletionChoice(BaseModel):
    """A single completion choice returned by the model"""
    index: int
    message: Message
    finish_reason: Optional[str] = None

class ChatCompletionUsage(BaseModel):
    """Token usage information for the completion"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    """Response format for chat completion endpoint"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage

# Streaming response models
class ChatCompletionChunkDelta(BaseModel):
    """Content delta for streaming responses"""
    content: Optional[str] = None
    role: Optional[str] = None

class ChatCompletionChunkChoice(BaseModel):
    """A single chunk choice for streaming"""
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None

class ChatCompletionChunk(BaseModel):
    """Chunk format for streaming responses"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    model: str
    choices: List[ChatCompletionChunkChoice]