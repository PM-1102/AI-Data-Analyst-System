"""
Logging System for DataSense AI
Structured logging for production debugging and monitoring
"""

import logging
import logging.handlers
import os
from pathlib import Path
from utils.config import Config


def setup_logger(name: str, level: str = None):
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (INFO, DEBUG, ERROR, etc.)
    
    Returns:
        Configured logger instance
    """
    
    if level is None:
        level = Config.LOG_LEVEL
    
    logger = logging.getLogger(name)
    
    # Set logging level
    logger.setLevel(getattr(logging, level))
    
    # Create logs directory if it doesn't exist
    log_dir = Path(Config.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    # ========== FILE HANDLER ==========
    file_handler = logging.handlers.RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=Config.LOG_MAX_SIZE_MB * 1024 * 1024,
        backupCount=Config.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(getattr(logging, level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # ========== CONSOLE HANDLER ==========
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger(__name__)


def log_exception(func_name: str, error: Exception):
    """
    Log exception with context
    
    Args:
        func_name: Function name where error occurred
        error: Exception object
    """
    logger.error(f"Error in {func_name}: {str(error)}", exc_info=True)


def log_performance(func_name: str, duration_ms: float):
    """
    Log performance metrics
    
    Args:
        func_name: Function name
        duration_ms: Duration in milliseconds
    """
    if duration_ms > 1000:  # Log if operation took more than 1 second
        logger.warning(f"Slow operation - {func_name} took {duration_ms:.2f}ms")


def log_security_event(event_type: str, details: str):
    """
    Log security-related events
    
    Args:
        event_type: Type of security event
        details: Event details (NO SENSITIVE DATA)
    """
    logger.warning(f"Security Event [{event_type}]: {details}")
