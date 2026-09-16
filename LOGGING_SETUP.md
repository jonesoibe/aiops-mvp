# Nexus AIOps Logging System Documentation

## Overview

The Nexus AIOps platform implements a comprehensive logging system using Python's `logging` module with daily file rotation and automatic archiving. All logs are written to the `logs/` directory with automatic rotation and cleanup.

## Features

✅ **Daily Log Rotation** - New log files created each day at midnight  
✅ **Automatic Archiving** - Old logs kept for 30 days then automatically cleaned up  
✅ **Multiple Log Files** - Separate logs for general, errors, API, and performance  
✅ **Detailed Formatting** - Timestamps, log levels, file names, line numbers, and messages  
✅ **Real-time Console Output** - Info and above levels logged to stdout  
✅ **Performance Tracking** - Automatically tracks slow requests and functions (>1 second)  
✅ **Security Logging** - Dedicated logging for authentication and security events  

## Log File Structure

```
logs/
├── nexus_aiops.log                    # Main application log
├── nexus_aiops_errors.log            # Error messages only
├── nexus_aiops_api.log               # API request/response log
└── nexus_aiops_performance.log       # Performance metrics and slow requests
```

### Daily Archive Format

```
logs/
├── nexus_aiops.log.2026-09-16        # Previous day's general log
├── nexus_aiops.log.2026-09-15        # Archive older days
├── nexus_aiops_errors.log.2026-09-16 # Previous day's errors
└── nexus_aiops_api.log.2026-09-16    # Previous day's API calls
```

## Log Levels

| Level | Usage | Console Output |
|-------|-------|-----------------|
| **DEBUG** | Detailed diagnostic information | No |
| **INFO** | General informational messages | Yes |
| **WARNING** | Warning messages, security events | Yes |
| **ERROR** | Error conditions | Yes |
| **CRITICAL** | Critical errors | Yes |

## Using the Logging System

### In Application Code

```python
from logger_config import get_logger, get_api_logger, get_performance_logger
from logging_utils import log_api_request, log_function_call, log_error_with_context

# Get loggers
logger = get_logger('nexus_aiops')
api_logger = get_api_logger()
perf_logger = get_performance_logger()

# Log messages
logger.info('Application started')
logger.warning('Warning message')
logger.error('Error occurred')

# Using decorators
@log_api_request
@app.route('/api/example')
def example_endpoint():
    return jsonify({'status': 'ok'})

@log_function_call
def important_function():
    pass

# Log errors with context
try:
    risky_operation()
except Exception as e:
    log_error_with_context(e, 'risky_operation()')
```

### Log Output Examples

**General Log (nexus_aiops.log):**
```
2026-09-16 08:30:45 - nexus_aiops - INFO - [nexus_app.py:98] - Starting Nexus AIOps v1.0.0
2026-09-16 08:30:46 - nexus_aiops - INFO - [logger_config.py:45] - Logging initialized for nexus_aiops
2026-09-16 08:31:12 - nexus_aiops - WARNING - [logging_utils.py:62] - SLOW FUNCTION: get_incident_data took 1.234s
```

**API Log (nexus_aiops_api.log):**
```
2026-09-16 09:15:30 - nexus_aiops.api - INFO - → [GET] /api/services | User: admin | IP: 127.0.0.1
2026-09-16 09:15:31 - nexus_aiops.api - INFO - ← [GET] /api/services | Status: 200 | Time: 0.145s | User: admin
2026-09-16 09:20:15 - nexus_aiops.api - ERROR - ✗ [POST] /api/auth/login | Error: Invalid credentials | Time: 0.023s | User: anonymous
```

**Error Log (nexus_aiops_errors.log):**
```
2026-09-16 10:45:22 - nexus_aiops - ERROR - [nexus_app.py:567] - Database connection failed: Connection refused
2026-09-16 10:45:22 - nexus_aiops - ERROR - Traceback (most recent call last):
  File "nexus_app.py", line 560, in connect_mongodb
    client = MongoClient(MONGODB_URI)
  ...
```

**Performance Log (nexus_aiops_performance.log):**
```
2026-09-16 11:20:10 - nexus_aiops.performance - DEBUG - [nexus_app.py:234] - Function get_topology_data completed in 0.856s
2026-09-16 11:21:45 - nexus_aiops.performance - WARNING - [logging_utils.py:73] - SLOW REQUEST: [GET] /api/incidents took 2.341s | User: admin
2026-09-16 11:30:22 - nexus_aiops.performance - DEBUG - [nexus_app.py:456] - Function analyze_incident completed in 1.567s
```

## Configuration

### Environment Variables

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Application environment
ENVIRONMENT=production
```

### Default Configuration

- **Log Directory**: `./logs/`
- **Log Level**: `INFO`
- **File Rotation**: Daily (midnight UTC)
- **Backup Count**: 30 days
- **Encoding**: UTF-8
- **Console Output**: INFO and above
- **File Output**: Full detail with timestamps

## Log Retention Policy

- **Active Logs**: Current day's logs
- **Archive Period**: 30 days (automatically deleted after 30 days)
- **Total Disk Space**: Approximately 100-500 MB depending on activity

## Monitoring Logs

### Real-time Log Monitoring

**Watch main log:**
```bash
tail -f logs/nexus_aiops.log
```

**Watch errors only:**
```bash
tail -f logs/nexus_aiops_errors.log
```

**Watch API calls:**
```bash
tail -f logs/nexus_aiops_api.log
```

**Search logs:**
```bash
grep "ERROR" logs/nexus_aiops.log
grep "admin" logs/nexus_aiops_api.log
grep "SLOW" logs/nexus_aiops_performance.log
```

### Log Analysis

**Count errors:**
```bash
grep -c "ERROR" logs/nexus_aiops.log
```

**Find slow requests:**
```bash
grep "SLOW REQUEST" logs/nexus_aiops_api.log
```

**List failed login attempts:**
```bash
grep "FAILED_LOGIN\|Invalid credentials" logs/nexus_aiops*.log
```

## Best Practices

1. **Use Appropriate Log Levels**
   - `DEBUG`: Detailed diagnostic information
   - `INFO`: General flow and milestones
   - `WARNING`: Recoverable issues and security events
   - `ERROR`: Problems that need attention
   - `CRITICAL`: System-level failures

2. **Include Context**
   ```python
   logger.error(f'Failed to process user {user_id}: {error_message}')
   ```

3. **Use Structured Logging**
   ```python
   logger.info(f'User login | Username: {username} | IP: {ip_address}')
   ```

4. **Log Security Events**
   ```python
   logger.warning(f'SECURITY: Failed login attempt | User: {username} | IP: {ip}')
   ```

5. **Avoid Logging Sensitive Data**
   - Don't log passwords or tokens
   - Don't log credit card numbers
   - Don't log personally identifiable information

## Troubleshooting

### Logs Not Writing
- Check `logs/` directory exists and is writable
- Verify filesystem permissions: `chmod 755 logs/`
- Check disk space: `df -h`

### Log Files Growing Too Large
- Check log level is not set to DEBUG
- Verify rotation is working: `ls -l logs/`
- Check for repeated error loops

### Missing Archive Files
- Verify rotation settings (should rotate at midnight)
- Check system time is correct
- Ensure 30-day rotation is working: `ls -lt logs/ | head -40`

## Advanced Configuration

### Changing Log Level at Runtime

```python
from logger_config import get_logger
logger = get_logger()
logger.setLevel(logging.DEBUG)  # Change to DEBUG
```

### Adding Custom Handlers

```python
import logging

logger = get_logger()
custom_handler = logging.handlers.RotatingFileHandler(
    'logs/custom.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
logger.addHandler(custom_handler)
```

### Integration with External Monitoring

The logging system can be extended to send logs to:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **DataDog**
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)

## Implementation Details

### Files

- **`logger_config.py`** - Core logging configuration with rotation
- **`logging_utils.py`** - Utility functions and decorators
- **`nexus_app.py`** - Integration with Flask application
- **`logs/`** - Directory containing all log files

### Key Components

1. **TimedRotatingFileHandler** - Rotates logs daily at midnight
2. **Separate Loggers** - Different loggers for different concerns
3. **Formatters** - Consistent, readable log messages
4. **Automatic Cleanup** - 30-day retention policy

## Performance Impact

The logging system is designed for minimal performance impact:
- Async logging where possible
- Buffered writes to disk
- Efficient rotation strategy
- Typical overhead: <1% CPU, <10MB memory

## Security Considerations

✅ Sensitive data never logged  
✅ File permissions restricted (readable by app only)  
✅ Security events logged separately  
✅ Audit trails maintained  
✅ Encrypted backups recommended for compliance  

## Support and Updates

For issues or enhancements:
1. Check logs for error messages
2. Review log retention settings
3. Verify disk space availability
4. Contact DevOps for external monitoring integration
