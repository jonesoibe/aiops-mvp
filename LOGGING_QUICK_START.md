# Nexus AIOps Logging - Quick Start Guide

## ✅ What's Been Implemented

A comprehensive daily rotating file logging system with:

- **Daily log rotation** at midnight UTC
- **30-day automatic archiving** with cleanup
- **4 separate log streams:**
  - `nexus_aiops.log` - General application logs
  - `nexus_aiops_errors.log` - Error messages only
  - `nexus_aiops_api.log` - API request/response tracking
  - `nexus_aiops_performance.log` - Performance metrics

- **Automatic performance monitoring** - Logs any request/function taking >1 second
- **Security event logging** - Dedicated logging for auth and security events
- **Real-time console output** - INFO and above levels to stdout
- **Rich formatting** - Timestamps, log levels, filenames, line numbers

## 📁 Log Files Location

```
project_root/
└── logs/
    ├── nexus_aiops.log              # Today's general log
    ├── nexus_aiops_errors.log       # Today's errors
    ├── nexus_aiops_api.log          # Today's API calls
    ├── nexus_aiops_performance.log  # Today's performance
    ├── nexus_aiops.log.2026-09-15   # Yesterday's general log
    ├── nexus_aiops_errors.log.2026-09-15
    └── ... (30 days of archives)
```

## 🚀 How to Use

### View Logs in Real-Time

```bash
# Watch main log
tail -f logs/nexus_aiops.log

# Watch errors
tail -f logs/nexus_aiops_errors.log

# Watch API calls
tail -f logs/nexus_aiops_api.log

# Watch performance metrics
tail -f logs/nexus_aiops_performance.log
```

### Search Logs

```bash
# Find errors
grep ERROR logs/nexus_aiops.log

# Find API calls to specific endpoint
grep "/api/auth" logs/nexus_aiops_api.log

# Find slow operations
grep "SLOW" logs/nexus_aiops_performance.log

# Find security events
grep "SECURITY" logs/nexus_aiops*.log
```

### Count Log Entries

```bash
# Count total log entries
wc -l logs/nexus_aiops.log

# Count errors
grep -c ERROR logs/nexus_aiops_errors.log

# Count slow requests
grep -c "SLOW REQUEST" logs/nexus_aiops_api.log
```

## 📊 Log Examples

### Application Startup
```
2026-09-16 08:30:45 - nexus_aiops - INFO - Logging initialized for nexus_aiops
2026-09-16 08:30:45 - nexus_aiops - INFO - Log directory: /path/to/logs
2026-09-16 08:30:45 - nexus_aiops - INFO - Log level: INFO
```

### API Request
```
2026-09-16 09:15:30 - nexus_aiops.api - INFO - → [GET] /api/services | User: admin | IP: 127.0.0.1
2026-09-16 09:15:31 - nexus_aiops.api - INFO - ← [GET] /api/services | Status: 200 | Time: 0.145s | User: admin
```

### Error
```
2026-09-16 10:45:22 - nexus_aiops - ERROR - [nexus_app.py:567] - Database connection failed
```

### Slow Request
```
2026-09-16 11:20:10 - nexus_aiops.api - WARNING - SLOW REQUEST: [POST] /api/incidents took 2.341s | User: admin
```

## 🛠️ Integration Points

The logging system is integrated at:

1. **Application Startup** - Logs startup information
2. **Flask Before/After Request** - Logs all API calls with timing
3. **Error Handlers** - Logs all exceptions with full context
4. **Security Events** - Logs authentication and authorization events
5. **Performance Tracking** - Automatically tracks slow operations

## 📝 Using in Code

### Basic Logging

```python
from logger_config import get_logger

logger = get_logger('nexus_aiops')

# Log messages
logger.info('User logged in')
logger.warning('High memory usage detected')
logger.error('Database connection failed')
```

### API Logging (Automatic)

```python
from logging_utils import log_api_request

@app.route('/api/example')
@log_api_request  # Automatically logs request/response
def example():
    return jsonify({'data': 'example'})
```

### Performance Tracking (Automatic)

```python
from logging_utils import log_function_call

@log_function_call  # Automatically logs execution time
def expensive_operation():
    # Long running code
    pass
```

### Error Logging

```python
from logging_utils import log_error_with_context

try:
    risky_operation()
except Exception as e:
    log_error_with_context(e, 'risky_operation()')
```

## ⚙️ Configuration

### Environment Variables

```bash
# Set log level (default: INFO)
export LOG_LEVEL=DEBUG

# Set environment
export ENVIRONMENT=production
```

### Programmatic Configuration

```python
from logger_config import get_logger

logger = get_logger('nexus_aiops')
logger.setLevel(logging.DEBUG)  # Change to DEBUG
```

## 🔍 Monitoring Guidelines

### Daily Checks

- **Error Count** - Should be minimal in production
- **API Response Times** - Should average <500ms
- **Slow Requests** - Any slow request indicates performance issue
- **Security Events** - Any failed login attempts should be reviewed

### Alert Thresholds

- **Error Rate** - Alert if >10 errors in 1 hour
- **Slow Requests** - Alert if >5 requests >2 seconds in 1 hour
- **Failed Logins** - Alert if >3 failed attempts from same IP
- **Disk Space** - Alert if logs exceed 500MB

## 📋 Log Retention

- **Active Period** - Today's logs actively written
- **Archive Period** - Previous 30 days kept in timestamped files
- **Cleanup** - Logs older than 30 days automatically deleted
- **Disk Space** - Typically 100-500MB depending on activity

## 🚀 Next Steps (Optional)

For external monitoring integration:

1. **ELK Stack** - Send logs to Elasticsearch
2. **Splunk** - Stream logs to Splunk
3. **CloudWatch** - Integrate with AWS CloudWatch
4. **DataDog** - Real-time monitoring dashboard
5. **Grafana** - Metrics visualization

## ✅ Verification

The logging system will automatically:

1. ✅ Create `logs/` directory on first run
2. ✅ Write daily log files
3. ✅ Rotate at midnight
4. ✅ Archive previous days
5. ✅ Clean up logs older than 30 days
6. ✅ Log all API requests and responses
7. ✅ Track slow operations (>1s)
8. ✅ Log errors with full stack traces
9. ✅ Output to console (INFO+) and files

## 📖 Full Documentation

See `LOGGING_SETUP.md` for:
- Detailed configuration options
- Advanced usage patterns
- Troubleshooting guide
- Performance considerations
- Security best practices
- Monitoring integration examples
