# Audit Trail & Application Logging System

## Overview

The Nexus AIOps platform includes a comprehensive audit trail and logging system for security, compliance, and operational monitoring. All user actions, API calls, security events, and application operations are logged to both files and an in-memory cache for quick retrieval.

## System Components

### 1. Audit Logger Module (`audit_logger.py`)

The core logging infrastructure with the following capabilities:

#### Log Files
- **`logs/audit_trail.log`** - All user actions and audit events
- **`logs/application.log`** - General application messages (DEBUG to INFO level)
- **`logs/errors.log`** - Error messages with stack traces
- **`logs/security.log`** - Security-related events and warnings

#### Key Classes

**`AuditEntry`** - Structured audit log entry with:
- Timestamp (UTC ISO format)
- Action type (LOGIN, CREATE, UPDATE, DELETE, REMEDIATE, etc.)
- User ID
- Resource type
- Status (success, failure, warning)
- Detailed information about the action
- IP address and User-Agent

**`AuditLogger`** - Central logging controller with methods:
- `log_audit(entry)` - Log an audit entry
- `log_action()` - Log a user action with details
- `log_app()` - Log application messages
- `log_error()` - Log errors with exceptions
- `log_security()` - Log security events
- `get_recent_audit_entries()` - Retrieve last N entries
- `get_audit_entries_by_user()` - Filter by user
- `get_audit_entries_by_action()` - Filter by action type
- `get_audit_entries_by_status()` - Filter by status

### 2. API Endpoints

#### Get Audit Log
```
GET /api/audit-log?limit=100&user_id=admin&action=LOGIN&status=success
```

Query parameters:
- `limit` - Number of entries to return (default: 100)
- `user_id` - Filter by user (optional)
- `action` - Filter by action type (optional)
- `status` - Filter by status: success/failure/warning (optional)

Response:
```json
{
  "total": 50,
  "entries": [
    {
      "timestamp": "2026-08-30T14:30:45.123456",
      "action": "LOGIN",
      "user_id": "admin",
      "resource": "authentication",
      "status": "success",
      "details": {"role": "admin"},
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "filters": {...}
}
```

#### Audit Statistics
```
GET /api/audit-log/stats
```

Response:
```json
{
  "total_entries": 1000,
  "success_count": 950,
  "failure_count": 30,
  "warning_count": 20,
  "unique_users": 15,
  "success_rate": 95.0,
  "failure_rate": 3.0,
  "top_actions": [
    ["LOGIN", 450],
    ["VIEW", 300],
    ["CREATE", 100]
  ],
  "top_users": [
    {"user_id": "admin", "count": 350},
    {"user_id": "operator", "count": 250}
  ]
}
```

#### Export Audit Log
```
GET /api/audit-log/export
```

Downloads audit logs as CSV file with columns:
- Timestamp
- Action
- User ID
- Resource
- Status
- IP Address
- Details (JSON)

### 3. Decorators

#### `@audit_required(action, resource_type)`

Automatically logs API actions:
```python
@app.route('/api/users', methods=['POST'])
@audit_required('CREATE', 'user')
@require_auth
def create_user(user=None):
    # Action is automatically logged as success/failure
    pass
```

## Audit Events

### Security Events
- **LOGIN** - User login (success/failure)
- **LOGOUT** - User logout
- **SECURITY_FAILED_LOGIN** - Failed login attempt
- **SECURITY_UNAUTHORIZED_ACCESS** - Unauthorized access attempt

### Data Events
- **CREATE** - Create new resource
- **UPDATE** - Modify existing resource
- **DELETE** - Delete resource
- **VIEW** - Access/view resource

### Operation Events
- **REMEDIATE** - Execute remediation action
- **SIMULATE** - Run simulation/test
- **EXPORT** - Export data
- **IMPORT** - Import data

## Audit Viewer Page

Access the audit trail viewer at: **`/audit`**

### Features

#### 1. Statistics Dashboard
- **Total Entries** - Complete audit log count
- **Success Rate** - Percentage of successful operations
- **Failure Rate** - Percentage of failed operations
- **Active Users** - Number of unique users in the log

#### 2. Advanced Filtering
Filter audit logs by:
- **User ID** - View actions by specific user
- **Action Type** - View specific action types
- **Status** - View successes, failures, or warnings

#### 3. Detailed Audit Table
- Timestamp (sortable)
- User ID (with badge)
- Action Type (with category badge)
- Resource Type
- Status (with color coding)
- IP Address
- Expandable Details Panel

#### 4. Export Functionality
- Download full audit log as CSV
- Includes all metadata and details
- Compatible with Excel, Google Sheets, etc.

## Logging in Code

### Example 1: Log a Simple Action
```python
from audit_logger import audit_logger

audit_logger.log_action(
    action='CREATE_RULE',
    user_id='admin',
    resource='detection_rule',
    status='success',
    details={'rule_name': 'CPU_SPIKE', 'threshold': 90},
    ip_address='192.168.1.100'
)
```

### Example 2: Log Application Messages
```python
from audit_logger import audit_logger

audit_logger.log_app('info', 'Simulation started with 5 instances')
audit_logger.log_app('debug', 'Database connection established')
audit_logger.log_app('warning', 'Slow query detected: 2500ms')
```

### Example 3: Log Errors
```python
from audit_logger import audit_logger

try:
    perform_operation()
except Exception as e:
    audit_logger.log_error('Operation failed', e)
```

### Example 4: Log Security Events
```python
from audit_logger import log_security_event

log_security_event(
    event_type='UNAUTHORIZED_ACCESS',
    message='Attempted access to admin panel',
    user_id='user123',
    details={'resource': '/admin/users', 'method': 'GET'}
)
```

## In-Memory Cache

The audit logger maintains the last 1000 entries in memory for:
- Fast retrieval of recent logs
- Real-time monitoring
- Dashboard statistics

Memory entries are automatically cleaned up when the limit is exceeded (FIFO).

## Log File Rotation

Each log file is automatically rotated when it reaches 10 MB:
- Previous files are archived with timestamps
- Last 10 versions of each log are kept
- Old files are automatically deleted

### Log File Locations
```
logs/
├── audit_trail.log          (Audit events)
├── application.log          (App messages)
├── errors.log              (Error stack traces)
└── security.log            (Security events)
```

## Security Considerations

### Data Protection
- IP addresses logged for audit trail
- User Agent logged for device/browser identification
- All timestamps in UTC for consistency
- No passwords or sensitive data logged

### Access Control
- Audit logs only accessible to authenticated users
- View `GET /audit` endpoint to see logs
- Export requires authentication

### Compliance
- All user actions logged for compliance audits
- 10-day retention of log files (configurable)
- Export capability for compliance reports
- Timestamped entries for incident investigation

## Performance

### Log Writing
- Asynchronous file I/O with buffering
- Rotating file handlers for performance
- Minimal impact on request latency

### Statistics Calculation
- Calculated from in-memory cache
- No database queries required
- Fast response times (< 100ms)

### Audit Viewer
- Loads up to 1000 entries in memory
- Client-side filtering and sorting
- Pagination for large datasets

## Configuration

### Changing Log Directory
```python
# In audit_logger.py
LOGS_DIR = Path(__file__).parent / 'logs'  # Change this
```

### Changing In-Memory Cache Size
```python
# In AuditLogger.__init__
self.max_memory_entries = 1000  # Change to desired size
```

### Changing Log File Rotation Size
```python
# In _create_*_logger methods
maxBytes=10*1024*1024,  # Change to desired size (in bytes)
backupCount=10          # Change number of backup files to keep
```

## Monitoring & Alerts

### Check Recent Errors
```python
from audit_logger import audit_logger

failures = audit_logger.get_audit_entries_by_status('failure')
print(f"Failed operations: {len(failures)}")
```

### Monitor User Activity
```python
admin_actions = audit_logger.get_audit_entries_by_user('admin')
print(f"Admin actions in session: {len(admin_actions)}")
```

### Track Specific Actions
```python
logins = audit_logger.get_audit_entries_by_action('LOGIN')
print(f"Logins in session: {len(logins)}")
```

## Troubleshooting

### "Permission Denied" when writing logs
- Ensure `logs/` directory exists and is writable
- Check file permissions: `ls -la logs/`
- On Windows: Right-click folder → Properties → Security

### Large log files growing too quickly
- Reduce `maxBytes` parameter in log handlers
- Increase rotation frequency by reducing the size
- Clean old log files manually: `rm logs/*.log.*`

### Memory usage growing too high
- Reduce `max_memory_entries` in AuditLogger
- Manually clear logs: `audit_logger.in_memory_log.clear()`

## Future Enhancements

Planned features:
- [ ] Real-time audit log streaming to dashboard
- [ ] Advanced search with regex support
- [ ] Audit log archival to cold storage
- [ ] Automated compliance report generation
- [ ] Audit trail visualization (timeline graphs)
- [ ] Alert rules for suspicious activities
- [ ] Integration with SIEM platforms

---

**Status**: ✅ Fully Implemented and Tested  
**Last Updated**: 2026-08-30  
**Version**: 1.0.0
