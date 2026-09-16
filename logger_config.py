"""
Logging configuration for Nexus AIOps
Implements daily rotating file logs with automatic archiving
"""

import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logging(app_name='nexus_aiops', log_level=logging.INFO):
    """
    Configure logging with daily rotation and archiving.

    Args:
        app_name: Name of the application for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """

    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler (STDOUT)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # Daily Rotating File Handler
    log_file = os.path.join(LOG_DIR, f'{app_name}.log')

    # TimedRotatingFileHandler rotates at midnight (00:00)
    # Keeps backups for 30 days (backupCount=30)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',  # Rotate at midnight
        interval=1,       # Every day
        backupCount=30,   # Keep 30 days of logs
        encoding='utf-8'
    )

    # Set the format for rotated filenames: app_name.log.2026-09-16
    file_handler.namer = lambda name: name.replace('.log', f'.log.{datetime.now().strftime("%Y-%m-%d")}')

    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # Separate Error File Handler
    error_log_file = os.path.join(LOG_DIR, f'{app_name}_errors.log')
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=error_log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.namer = lambda name: name.replace('_errors.log', f'_errors.log.{datetime.now().strftime("%Y-%m-%d")}')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)

    # API Access Log Handler (separate file for API requests)
    api_log_file = os.path.join(LOG_DIR, f'{app_name}_api.log')
    api_handler = logging.handlers.TimedRotatingFileHandler(
        filename=api_log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    api_handler.namer = lambda name: name.replace('_api.log', f'_api.log.{datetime.now().strftime("%Y-%m-%d")}')
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(detailed_formatter)

    # Create separate API logger
    api_logger = logging.getLogger(f'{app_name}.api')
    api_logger.setLevel(logging.INFO)
    api_logger.handlers.clear()
    api_logger.addHandler(api_handler)
    api_logger.propagate = False

    # Performance Log Handler (for performance tracking)
    perf_log_file = os.path.join(LOG_DIR, f'{app_name}_performance.log')
    perf_handler = logging.handlers.TimedRotatingFileHandler(
        filename=perf_log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    perf_handler.namer = lambda name: name.replace('_performance.log', f'_performance.log.{datetime.now().strftime("%Y-%m-%d")}')
    perf_handler.setLevel(logging.DEBUG)
    perf_handler.setFormatter(detailed_formatter)

    # Create separate performance logger
    perf_logger = logging.getLogger(f'{app_name}.performance')
    perf_logger.setLevel(logging.DEBUG)
    perf_logger.handlers.clear()
    perf_logger.addHandler(perf_handler)
    perf_logger.propagate = False

    # Log initialization message
    logger.info(f'Logging initialized for {app_name}')
    logger.info(f'Log directory: {LOG_DIR}')
    logger.info(f'Log level: {logging.getLevelName(log_level)}')

    return logger

def get_logger(name='nexus_aiops'):
    """Get a logger instance by name."""
    return logging.getLogger(name)

def get_api_logger(name='nexus_aiops.api'):
    """Get the API logger instance."""
    return logging.getLogger(name)

def get_performance_logger(name='nexus_aiops.performance'):
    """Get the performance logger instance."""
    return logging.getLogger(name)

# Initialize default logger on module import
default_logger = setup_logging()
