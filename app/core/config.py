from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "Bedrock API Bridge"
    PROJECT_DESCRIPTION: str = "A secure bridge between frontend applications and AWS Bedrock AI models"
    VERSION: str = "1.0.0"
    API_PREFIX: str = ""
    SHOW_DOCS: bool = True
    
    # Security settings
    API_KEYS: List[str] = []
    
    @validator("API_KEYS", pre=True)
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            return [key.strip() for key in v.split(",") if key.strip()]
        return v
        
    # AWS settings
    AWS_REGION: str = "us-east-1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Model settings
    DEFAULT_MODEL: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    DEFAULT_MAX_TOKENS: int = 2000
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Usage tracking
    TRACK_USAGE: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()