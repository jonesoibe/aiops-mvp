# User Management Guide - Nexus AIOps

This guide covers user management operations including creating, modifying, and deleting users.

## User Management Operations

### 1. Create a New User

**Via Web Interface (Signup):**
1. Navigate to `http://localhost:5000/login`
2. Click "Sign Up" link
3. Fill in user details:
   - Email
   - First Name
   - Last Name
   - Username
   - Password (strong password required)
   - Role (User or Tester)
   - Department
4. Verify email with 6-digit code sent to inbox
5. Account is created and ready to use

**Via API:**
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePassword123!",
    "role": "user",
    "department": "Engineering"
  }'
```

### 2. Update User Profile

**Via Web Interface:**
1. Log in to your account
2. Click on "Profile" (user icon)
3. Update your details:
   - First Name
   - Last Name
   - Department
4. Click "Save Changes"

**Via API:**
```bash
curl -X POST http://localhost:5000/api/user/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "department": "Operations"
  }'
```

### 3. Change Password

**Via Web Interface:**
1. Log in to your account
2. Go to Profile settings
3. Click "Change Password"
4. Enter:
   - Current password
   - New password
   - Confirm new password
5. Click "Update Password"

**Via API:**
```bash
curl -X POST http://localhost:5000/api/user/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "current_password": "OldPassword123!",
    "new_password": "NewPassword456!"
  }'
```

### 4. Delete a User (Admin Only)

**Requirements:**
- ✓ Admin role required
- ✓ Cannot delete your own account
- ✓ Cannot delete the last admin user
- ✓ Requires valid JWT token

**Via API:**
```bash
curl -X DELETE http://localhost:5000/api/admin/users/<username> \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Example:**
```bash
# Delete user "testuser" as admin
curl -X DELETE http://localhost:5000/api/admin/users/testuser \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "message": "User testuser has been deleted successfully",
  "deleted_user": {
    "username": "testuser",
    "email": "testuser@example.com",
    "role": "user"
  }
}
```

**Error Responses:**
- `403 Forbidden` - User is not an admin
- `400 Bad Request` - Trying to delete yourself or the last admin
- `404 Not Found` - User doesn't exist
- `500 Server Error` - Database error

### 5. Forgot Password

**Via Web Interface:**
1. Click "Forgot Password" on login page
2. Enter your email address
3. Verify with 6-digit code sent to email
4. Set your new password
5. Log in with new password

**Via API:**
```bash
# Request password reset
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Reset password with code
curl -X POST http://localhost:5000/api/auth/password-reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "code": "123456",
    "new_password": "NewPassword123!"
  }'
```

## User Roles & Permissions

### Admin
- ✓ Full access to all features
- ✓ Can create/delete alert rules
- ✓ Can manage SLOs
- ✓ Can delete users
- ✓ Can access admin settings
- ✓ Cannot be deleted if it's the last admin

### User
- ✓ Can view dashboard
- ✓ Can view incidents and topology
- ✓ Can trigger analysis and remediation
- ✓ Can manage own profile
- ✓ Limited configuration access

### Tester
- ✓ Can view all data
- ✓ Can run simulations
- ✓ Can trigger analysis
- ✓ Read-only configuration access

## Departments

Available departments for user assignment:
- Engineering
- Operations
- DevOps
- Quality Assurance
- Security
- Data Engineering
- Management
- Other

## Database Interaction

### Direct Database User Deletion (MongoDB)

If you need to delete users directly from MongoDB:

```bash
# Connect to MongoDB
mongo "mongodb+srv://aiops_user:admin123@altschool.m511v.mongodb.net/nexus_aiops"

# Delete a user
db.users.deleteOne({username: "username"})

# Verify deletion
db.users.findOne({username: "username"})  # Should return null

# List all users
db.users.find({}, {username: 1, email: 1, role: 1})
```

### In-Memory Storage

If using in-memory storage (no MongoDB), user data is stored in the application memory and is lost on restart.

## Demo Users

Default demo users created on first run:

| Username | Password | Email | Role |
|----------|----------|-------|------|
| admin | admin123 | admin@nexus.local | admin |
| operator | operator123 | operator@nexus.local | operator |
| viewer | viewer123 | viewer@nexus.local | viewer |

> **Warning**: Change these default credentials in production!

## Security Best Practices

1. **Strong Passwords Required**
   - Minimum 8 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Cannot be blank or common words

2. **Admin Account Protection**
   - Don't share admin credentials
   - Regular password changes recommended
   - At least one admin must exist at all times

3. **Audit Trail**
   - All user operations are logged
   - Check audit logs for suspicious activity
   - Log location: `logs/nexus_audit.log`

4. **HTTPS/TLS Encryption**
   - All credentials encrypted in transit
   - Use HTTPS in production
   - Self-signed certs for development only

## Troubleshooting

### User Cannot Log In
- Verify username and password are correct
- Check if user account exists
- Verify user email is confirmed (if signup required verification)
- Check server logs for errors

### Cannot Delete a User
- Verify you have admin role
- Cannot delete your own account
- Cannot delete last admin user
- Check if username exists

### Password Reset Not Received
- Check spam/junk folder
- Verify email address in system
- Check SMTP configuration in `.env`
- Review server logs for email errors

### User Account Locked
- Currently no auto-lock feature
- Locked accounts would need manual reset
- Request admin to reset password or delete/recreate account

## API Reference

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/signup` | None | Create new account |
| POST | `/api/auth/login` | None | Authenticate user |
| POST | `/api/auth/verify-email` | None | Verify email address |
| POST | `/api/auth/forgot-password` | None | Request password reset |
| POST | `/api/auth/password-reset` | None | Reset password |
| GET | `/api/user/profile` | Required | Get user profile |
| POST | `/api/user/profile` | Required | Update user profile |
| POST | `/api/user/change-password` | Required | Change password |
| DELETE | `/api/admin/users/<username>` | Admin | Delete user |

## Support

For issues with user management:
1. Check the audit logs in `logs/nexus_audit.log`
2. Review API response error messages
3. Check server logs for detailed error information
4. Verify database connectivity (if using MongoDB)

---

**Last Updated:** 2026-09-16
**Version:** 1.0
