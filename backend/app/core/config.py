"""
Configuration management untuk backend AI service.
Menggunakan pydantic-settings untuk type-safe config.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import Union


class Settings(BaseSettings):
    """Application settings dengan environment variable support."""
    
    # API Configuration
    api_title: str = "AI E-commerce Backend"
    api_version: str = "1.0.0"
    api_description: str = "AI-powered product listing automation"
    
    # CORS Settings
    cors_origins: Union[list[str], str] = ["http://localhost:3000", "http://localhost:3001"]
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # AI Model Configuration
    openai_api_key: str
    openai_api_base: str
    openai_model_name: str = "gpt-4-vision-preview"
    use_mock_ai: bool = False  # For testing when API is unavailable
    
    # Google Search API Configuration
    google_search_api_key: str = ""
    google_search_engine_id: str = ""
    google_search_enabled: bool = True
    
    # Supabase Configuration
    supabase_url: str
    supabase_key: str  # Service role key for backend
    supabase_anon_key: str = ""  # Optional: for client-side auth
    
    # File Upload
    upload_dir: str = "uploads"
    max_file_size_mb: int = 10
    
    # Marketplace Mock Config
    marketplace_mock_delay: float = 1.0  # Simulasi network delay
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance untuk performa.
    Hanya load .env sekali saja.
    """
    return Settings()
