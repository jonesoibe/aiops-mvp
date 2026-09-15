"""
Authentication Manager for Nexus AIOps
Handles user registration, email verification, and role management
"""

import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import hashlib
import hmac

class AuthenticationManager:
    """Manages user authentication, registration, and email verification."""

    # Email regex pattern
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Valid roles
    VALID_ROLES = ['admin', 'tester', 'user', 'viewer']

    # Valid departments
    VALID_DEPARTMENTS = [
        'Engineering',
        'Operations',
        'DevOps',
        'Quality Assurance',
        'Security',
        'Data Engineering',
        'Management',
        'Other'
    ]

    # Verification code expiry (15 minutes)
    VERIFICATION_CODE_EXPIRY = 900

    def __init__(self):
        """Initialize the authentication manager."""
        self.verification_codes = {}  # email -> {code, expiry, attempts}
        self.temp_users = {}  # email -> user_data
        self.reset_tokens = {}  # token -> {email, expiry}

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not email or len(email) > 255:
            return False, "Email must be between 1 and 255 characters"

        if not re.match(AuthenticationManager.EMAIL_PATTERN, email):
            return False, "Invalid email format"

        return True, "Email is valid"

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if len(password) > 128:
            return False, "Password must not exceed 128 characters"

        # Check for complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain uppercase, lowercase, and numbers"

        return True, "Password is strong"

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format.

        Args:
            username: Username to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long"

        if len(username) > 50:
            return False, "Username must not exceed 50 characters"

        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, hyphens, and underscores"

        return True, "Username is valid"

    @staticmethod
    def validate_role(role: str) -> Tuple[bool, str]:
        """
        Validate user role.

        Args:
            role: Role to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if role.lower() not in AuthenticationManager.VALID_ROLES:
            return False, f"Invalid role. Must be one of: {', '.join(AuthenticationManager.VALID_ROLES)}"

        return True, "Role is valid"

    @staticmethod
    def validate_department(department: str) -> Tuple[bool, str]:
        """
        Validate department.

        Args:
            department: Department to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if department not in AuthenticationManager.VALID_DEPARTMENTS:
            return False, f"Invalid department. Must be one of: {', '.join(AuthenticationManager.VALID_DEPARTMENTS)}"

        return True, "Department is valid"

    def generate_verification_code(self, email: str) -> str:
        """
        Generate a 6-digit verification code.

        Args:
            email: Email to generate code for

        Returns:
            6-digit verification code
        """
        code = ''.join(secrets.choice('0123456789') for _ in range(6))
        expiry = datetime.utcnow() + timedelta(seconds=self.VERIFICATION_CODE_EXPIRY)

        self.verification_codes[email] = {
            'code': code,
            'expiry': expiry,
            'attempts': 0
        }

        return code

    def verify_email_code(self, email: str, code: str) -> Tuple[bool, str]:
        """
        Verify the email verification code.

        Args:
            email: Email address
            code: Verification code

        Returns:
            Tuple of (is_valid, message)
        """
        if email not in self.verification_codes:
            return False, "No verification code found for this email. Request a new one."

        vc = self.verification_codes[email]

        # Check expiry
        if datetime.utcnow() > vc['expiry']:
            del self.verification_codes[email]
            return False, "Verification code has expired. Request a new one."

        # Check attempts
        if vc['attempts'] >= 5:
            del self.verification_codes[email]
            return False, "Too many failed attempts. Request a new verification code."

        # Check code
        if vc['code'] != code:
            vc['attempts'] += 1
            return False, f"Invalid verification code. {5 - vc['attempts']} attempts remaining."

        # Code is valid - remove it and return success
        del self.verification_codes[email]
        return True, "Email verified successfully"

    def store_temp_user(self, email: str, user_data: Dict) -> None:
        """
        Store temporary user data pending email verification.

        Args:
            email: Email address
            user_data: User data dictionary
        """
        self.temp_users[email] = {
            **user_data,
            'created_at': datetime.utcnow().isoformat(),
            'verified_at': None
        }

    def get_temp_user(self, email: str) -> Optional[Dict]:
        """
        Retrieve temporary user data.

        Args:
            email: Email address

        Returns:
            User data or None
        """
        return self.temp_users.get(email)

    def mark_email_verified(self, email: str) -> None:
        """
        Mark email as verified.

        Args:
            email: Email address
        """
        if email in self.temp_users:
            self.temp_users[email]['verified_at'] = datetime.utcnow().isoformat()

    def get_verified_user(self, email: str) -> Optional[Dict]:
        """
        Get a verified user's data.

        Args:
            email: Email address

        Returns:
            User data if verified, None otherwise
        """
        user = self.temp_users.get(email)
        if user and user.get('verified_at'):
            return user
        return None

    def remove_temp_user(self, email: str) -> None:
        """
        Remove temporary user data.

        Args:
            email: Email address
        """
        if email in self.temp_users:
            del self.temp_users[email]

    def generate_reset_token(self, email: str) -> str:
        """
        Generate a password reset token.

        Args:
            email: User email

        Returns:
            Reset token
        """
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(hours=1)
        self.reset_tokens[token] = {
            'email': email,
            'expiry': expiry
        }
        return token

    def verify_reset_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Verify a password reset token.

        Args:
            token: Reset token

        Returns:
            Tuple of (is_valid, email)
        """
        if token not in self.reset_tokens:
            return False, None

        rt = self.reset_tokens[token]

        # Check expiry
        if datetime.utcnow() > rt['expiry']:
            del self.reset_tokens[token]
            return False, None

        return True, rt['email']

    def use_reset_token(self, token: str) -> None:
        """
        Invalidate a reset token after use.

        Args:
            token: Reset token
        """
        if token in self.reset_tokens:
            del self.reset_tokens[token]

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt (or fallback to PBKDF2).

        Args:
            password: Password to hash

        Returns:
            Hashed password
        """
        try:
            import bcrypt
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        except ImportError:
            # Fallback to PBKDF2
            import hashlib
            salt = secrets.token_hex(16)
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return f"pbkdf2${salt}${hash_obj.hex()}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Password to verify
            password_hash: Password hash

        Returns:
            True if password matches
        """
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except ImportError:
            # Fallback to PBKDF2
            if password_hash.startswith('pbkdf2$'):
                parts = password_hash.split('$')
                if len(parts) == 3:
                    salt = parts[1]
                    stored_hash = parts[2]
                    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
                    return hash_obj.hex() == stored_hash
            return False


# Create global instance
auth_manager = AuthenticationManager()
