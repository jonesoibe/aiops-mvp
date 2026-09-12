#!/usr/bin/env python3
"""
Audit Trail and Application Logging System
Comprehensive logging for security, compliance, and debugging
"""

import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps

# Create logs directory
LOGS_DIR = Path(__file__).parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Audit trail file
AUDIT_LOG_FILE = LOGS_DIR / 'audit_trail.log'
APPLICATION_LOG_FILE = LOGS_DIR / 'application.log'
ERROR_LOG_FILE = LOGS_DIR / 'errors.log'
SECURITY_LOG_FILE = LOGS_DIR / 'security.log'


class AuditEntry:
    """Structured audit log entry"""

    def __init__(self,
                 action: str,
                 user_id: str,
                 resource: str,
                 status: str,
                 details: Dict[str, Any],
                 ip_address: Optional[str] = None,
                 user_agent: Optional[str] = None):
        self.timestamp = datetime.utcnow().isoformat()
        self.action = action
        self.user_id = user_id
        self.resource = resource
        self.status = status  # 'success', 'failure', 'warning'
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'action': self.action,
            'user_id': self.user_id,
            'resource': self.resource,
            'status': self.status,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class AuditLogger:
    """Centralized audit logging"""

    def __init__(self):
        self.audit_logger = self._create_audit_logger()
        self.app_logger = self._create_app_logger()
        self.error_logger = self._create_error_logger()
        self.security_logger = self._create_security_logger()
        self.in_memory_log = []  # Keep recent logs in memory for quick access
        self.max_memory_entries = 1000

    def _create_audit_logger(self) -> logging.Logger:
        """Create audit trail logger"""
        logger = logging.getLogger('audit')
        logger.setLevel(logging.INFO)

        # File handler with rotation
        handler = logging.handlers.RotatingFileHandler(
            AUDIT_LOG_FILE,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _create_app_logger(self) -> logging.Logger:
        """Create application logger"""
        logger = logging.getLogger('app')
        logger.setLevel(logging.DEBUG)

        # File handler with rotation
        handler = logging.handlers.RotatingFileHandler(
            APPLICATION_LOG_FILE,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )

        formatter = logging.Formatter(
            '%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _create_error_logger(self) -> logging.Logger:
        """Create error logger"""
        logger = logging.getLogger('error')
        logger.setLevel(logging.ERROR)

        # File handler with rotation
        handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s\n%(exc_info)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _create_security_logger(self) -> logging.Logger:
        """Create security logger"""
        logger = logging.getLogger('security')
        logger.setLevel(logging.WARNING)

        # File handler with rotation
        handler = logging.handlers.RotatingFileHandler(
            SECURITY_LOG_FILE,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )

        formatter = logging.Formatter(
            '%(asctime)s | SECURITY | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def log_audit(self, entry: AuditEntry):
        """Log audit entry"""
        # Log to file
        self.audit_logger.info(entry.to_json())

        # Keep in memory
        self.in_memory_log.append(entry.to_dict())
        if len(self.in_memory_log) > self.max_memory_entries:
            self.in_memory_log.pop(0)

    def log_action(self,
                   action: str,
                   user_id: str,
                   resource: str,
                   status: str,
                   details: Dict[str, Any],
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None):
        """Log an action"""
        entry = AuditEntry(
            action=action,
            user_id=user_id,
            resource=resource,
            status=status,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.log_audit(entry)

    def log_app(self, level: str, message: str, **kwargs):
        """Log application message"""
        logger_method = getattr(self.app_logger, level.lower(), self.app_logger.info)
        logger_method(message)

    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log error"""
        if exception:
            self.error_logger.error(message, exc_info=exception)
        else:
            self.error_logger.error(message)

    def log_security(self, level: str, message: str):
        """Log security event"""
        logger_method = getattr(self.security_logger, level.lower(), self.security_logger.warning)
        logger_method(message)

    def get_recent_audit_entries(self, limit: int = 100) -> list:
        """Get recent audit entries from memory"""
        return self.in_memory_log[-limit:]

    def get_audit_entries_by_user(self, user_id: str, limit: int = 50) -> list:
        """Get audit entries for a specific user"""
        return [entry for entry in self.in_memory_log if entry['user_id'] == user_id][-limit:]

    def get_audit_entries_by_action(self, action: str, limit: int = 50) -> list:
        """Get audit entries for a specific action"""
        return [entry for entry in self.in_memory_log if entry['action'] == action][-limit:]

    def get_audit_entries_by_status(self, status: str, limit: int = 50) -> list:
        """Get audit entries with a specific status"""
        return [entry for entry in self.in_memory_log if entry['status'] == status][-limit:]


# Global audit logger instance
audit_logger = AuditLogger()


def audit_required(action: str, resource_type: str = 'unknown'):
    """Decorator to automatically log API actions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                from flask import request, g
                # Extract user info from request context
                user_id = getattr(g, 'user_id', 'anonymous')
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', 'unknown')
            except RuntimeError:
                # Not in Flask context
                user_id = 'anonymous'
                ip_address = 'unknown'
                user_agent = 'unknown'

            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Log successful action
                audit_logger.log_action(
                    action=action,
                    user_id=user_id,
                    resource=resource_type,
                    status='success',
                    details={
                        'method': request.method,
                        'path': request.path,
                        'response_status': getattr(result, 'status_code', 200) if hasattr(result, 'status_code') else 200
                    },
                    ip_address=ip_address,
                    user_agent=user_agent
                )

                return result
            except Exception as e:
                # Log failed action
                audit_logger.log_action(
                    action=action,
                    user_id=user_id,
                    resource=resource_type,
                    status='failure',
                    details={
                        'method': request.method,
                        'path': request.path,
                        'error': str(e)
                    },
                    ip_address=ip_address,
                    user_agent=user_agent
                )

                # Log the error
                audit_logger.log_error(f"Error in {action}: {str(e)}", e)

                raise

        return wrapper
    return decorator


def log_security_event(event_type: str, message: str, user_id: str = 'unknown', details: Optional[Dict] = None):
    """Log security-related events"""
    try:
        from flask import request
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
    except RuntimeError:
        ip_address = 'unknown'
        user_agent = 'unknown'

    security_message = f"[{event_type}] User: {user_id} | IP: {ip_address} | {message}"
    audit_logger.log_security('warning', security_message)

    # Also log to audit trail
    audit_logger.log_action(
        action=f'SECURITY_{event_type}',
        user_id=user_id,
        resource='security',
        status='warning',
        details=details or {'message': message},
        ip_address=ip_address,
        user_agent=user_agent
    )


# Export functions
__all__ = [
    'AuditLogger',
    'AuditEntry',
    'audit_logger',
    'audit_required',
    'log_security_event',
    'AUDIT_LOG_FILE',
    'APPLICATION_LOG_FILE',
    'ERROR_LOG_FILE',
    'SECURITY_LOG_FILE',
    'LOGS_DIR'
]
