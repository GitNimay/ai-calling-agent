"""
Configuration module for AI Calling Agent.
Loads environment variables and provides application settings.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Gemini API Configuration
    GEMINI_API_KEY: str
    GEMINI_MODEL_TEXT: str = "gemini-2.5-flash"
    GEMINI_MODEL_LIVE: str = "gemini-2.5-flash"
    
    # Server Configuration
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    RELOAD: bool = True
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1
    
    # Twilio Configuration (Optional - for Phase 5)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings: Application settings object
    """
    return settings
