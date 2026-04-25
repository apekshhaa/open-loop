"""
Configuration module for the AI Agent Credit System.

Loads environment variables and provides configuration settings
for the application, database, blockchain, and other services.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class uses pydantic_settings to automatically load
    configuration from .env files and environment variables.
    """
    
    # Application Settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    api_title: str = os.getenv("API_TITLE", "AI Agent Credit System")
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    
    # Server Settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Database Configuration
    mongodb_url: Optional[str] = os.getenv("MONGODB_URL", None)
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL", None)
    supabase_api_key: Optional[str] = os.getenv("SUPABASE_API_KEY", None)
    
    # Blockchain/Testnet Configuration
    blockchain_provider_url: Optional[str] = os.getenv("BLOCKCHAIN_PROVIDER_URL", None)
    ethereum_testnet: str = os.getenv("ETHEREUM_TESTNET", "sepolia")
    wallet_address: Optional[str] = os.getenv("WALLET_ADDRESS", None)
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
