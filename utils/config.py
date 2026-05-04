"""
Configuration Management for DataSense AI
Handles all application settings in one place
"""

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()


class Config:
    """Production configuration"""
    
    # ========== APPLICATION SETTINGS ==========
    APP_NAME = "DataSense AI"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Professional AI Data Analysis Platform"
    
    # ========== UI SETTINGS ==========
    PAGE_LAYOUT = "wide"
    SIDEBAR_INITIAL_STATE = "expanded"
    THEME = "dark"
    
    # ========== FILE UPLOAD SETTINGS ==========
    MAX_FILE_SIZE_MB = 100  # Maximum file upload size
    ALLOWED_EXTENSIONS = ["csv", "xlsx", "xls", "json"]
    UPLOAD_TIMEOUT_SECONDS = 60
    
    # ========== DATA PROCESSING SETTINGS ==========
    MAX_ROWS_FOR_FULL_ANALYSIS = 100000  # Warn if dataset is larger
    CACHE_ENABLED = True
    CACHE_TTL_HOURS = 1
    
    # ========== LLM SETTINGS ==========
    LLM_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    LLM_TEMPERATURE = 0.2  # Lower = more factual
    LLM_MAX_TOKENS = 1000
    LLM_TIMEOUT_SECONDS = 30
    
    # ========== SECURITY SETTINGS ==========
    ENFORCE_HTTPS = True  # For deployment
    SESSION_TIMEOUT_MINUTES = 30
    MAX_SESSION_DATA_MB = 500  # Max session memory
    
    # ========== LOGGING SETTINGS ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/datasense.log"
    LOG_MAX_SIZE_MB = 10
    LOG_BACKUP_COUNT = 5
    
    # ========== DEPLOYMENT SETTINGS ==========
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
    ANALYTICS_ENABLED = True
    
    @classmethod
    def get_groq_api_key(cls):
        """
        Get API key from Streamlit secrets or environment
        Prioritizes Streamlit secrets for security
        """
        try:
            # Try Streamlit secrets first (production)
            return st.secrets.get("GROQ_API_KEY")
        except:
            # Fallback to environment variable (development)
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY not found. Set it in Streamlit secrets or .env file"
                )
            return api_key
    
    @classmethod
    def validate_file_size(cls, file_size_bytes):
        """Validate if file size is within limits"""
        max_bytes = cls.MAX_FILE_SIZE_MB * 1024 * 1024
        return file_size_bytes <= max_bytes
    
    @classmethod
    def is_production(cls):
        """Check if running in production"""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls):
        """Check if running in development"""
        return cls.ENVIRONMENT == "development"


def get_config():
    """Get configuration instance"""
    return Config()
