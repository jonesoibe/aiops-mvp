"""
Logging utilities for Flask application
Provides decorators and helpers for comprehensive logging
"""

import time
import logging
from functools import wraps
from flask import request, g
from logger_config import get_logger, get_api_logger, get_performance_logger

logger = get_logger('nexus_aiops')
api_logger = get_api_logger()
perf_logger = get_performance_logger()

def log_api_request(f):
    """
    Decorator to log API requests and responses.
    Logs request method, endpoint, parameters, response status, and response time.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        # Extract request details
        method = request.method
        endpoint = request.path
        remote_addr = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')

        # Extract user from request context if available
        user = getattr(g, 'user', None)
        username = user['username'] if user else 'anonymous'

        # Log incoming request
        api_logger.info(
            f'→ [{method}] {endpoint} | User: {username} | IP: {remote_addr}'
        )

        try:
            # Execute the route function
            response = f(*args, **kwargs)

            # Calculate response time
            response_time = time.time() - start_time

            # Determine status code
            status_code = 200
            if isinstance(response, tuple) and len(response) > 1:
                status_code = response[1]
            elif hasattr(response, 'status_code'):
                status_code = response.status_code

            # Log successful response
            api_logger.info(
                f'← [{method}] {endpoint} | Status: {status_code} | Time: {response_time:.3f}s | User: {username}'
            )

            # Log performance metrics for slow requests (> 1 second)
            if response_time > 1.0:
                perf_logger.warning(
                    f'SLOW REQUEST: [{method}] {endpoint} took {response_time:.3f}s | User: {username}'
                )

            return response

        except Exception as e:
            response_time = time.time() - start_time
            api_logger.error(
                f'✗ [{method}] {endpoint} | Error: {str(e)} | Time: {response_time:.3f}s | User: {username}'
            )
            raise

    return decorated_function

def log_function_call(f):
    """
    Decorator to log function calls with arguments and execution time.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        func_name = f.__name__

        logger.debug(f'Calling function: {func_name}')

        try:
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time

            logger.debug(f'Function {func_name} completed in {execution_time:.3f}s')

            if execution_time > 0.5:
                perf_logger.debug(
                    f'SLOW FUNCTION: {func_name} took {execution_time:.3f}s'
                )

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f'Function {func_name} failed after {execution_time:.3f}s: {str(e)}'
            )
            raise

    return decorated_function

def log_database_operation(operation_type, details=''):
    """
    Log database operations.

    Args:
        operation_type: Type of operation (INSERT, UPDATE, DELETE, QUERY, etc.)
        details: Additional details about the operation
    """
    logger.info(f'DB {operation_type}: {details}')

def log_security_event(event_type, details='', username='unknown'):
    """
    Log security-related events.

    Args:
        event_type: Type of security event (LOGIN, LOGOUT, FAILED_LOGIN, UNAUTHORIZED_ACCESS, etc.)
        details: Additional details about the event
        username: Username associated with the event
    """
    logger.warning(
        f'SECURITY EVENT [{event_type}] | User: {username} | Details: {details}'
    )

def log_error_with_context(error, context=''):
    """
    Log an error with full context information.

    Args:
        error: The exception/error to log
        context: Additional context about where the error occurred
    """
    logger.error(
        f'ERROR in {context}: {str(error)}',
        exc_info=True
    )

def log_startup_info(app_name='Nexus AIOps', version='1.0.0', config_info=''):
    """Log application startup information."""
    logger.info('=' * 60)
    logger.info(f'Starting {app_name} v{version}')
    logger.info(f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    if config_info:
        logger.info(f'Configuration: {config_info}')
    logger.info('=' * 60)

def log_shutdown_info(app_name='Nexus AIOps', uptime_seconds=0):
    """Log application shutdown information."""
    logger.info('=' * 60)
    logger.info(f'Shutting down {app_name}')
    if uptime_seconds:
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        logger.info(f'Uptime: {int(hours)}h {int(minutes)}m')
    logger.info(f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info('=' * 60)

def configure_flask_logging(app):
    """
    Configure Flask to use the custom logging system.

    Args:
        app: Flask application instance
    """
    # Disable default Flask logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)

    # Add a before_request handler to log all requests
    @app.before_request
    def log_request_info():
        g.start_time = time.time()
        api_logger.debug(
            f'Request: {request.method} {request.path} | '
            f'From: {request.remote_addr} | '
            f'User-Agent: {request.user_agent}'
        )

    # Add an after_request handler to log response info
    @app.after_request
    def log_response_info(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            api_logger.info(
                f'Response: {request.method} {request.path} | '
                f'Status: {response.status_code} | '
                f'Time: {elapsed:.3f}s'
            )
        return response

# Initialize startup logging
if __name__ != '__main__':
    logger.info('Logging utils module loaded')
