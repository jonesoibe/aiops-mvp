import time
from collections import defaultdict, deque
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

class TokenBucketLimiter:
    """Token Bucket algorithm for rate limiting (allows bursts)"""
    
    def __init__(self, rate: float, capacity: float):
        """
        Args:
            rate: tokens per second
            capacity: max tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        now = time.time()
        elapsed = now - self.last_update
        
        # Add new tokens
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
    
    def get_wait_time(self) -> float:
        """Get seconds to wait before next token is available"""
        if self.tokens >= 1:
            return 0
        return (1 - self.tokens) / self.rate


class SlidingWindowLimiter:
    """Sliding Window algorithm (strict limit, no bursts)"""
    
    def __init__(self, rate: int, window_seconds: int):
        """
        Args:
            rate: max requests in window
            window_seconds: time window in seconds
        """
        self.rate = rate
        self.window = window_seconds
        self.requests = deque()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Remove old requests outside window
        while self.requests and self.requests[0] <= now - self.window:
            self.requests.popleft()
        
        if len(self.requests) < self.rate:
            self.requests.append(now)
            return True
        return False
    
    def get_wait_time(self) -> float:
        """Get seconds to wait before next request is allowed"""
        if not self.requests:
            return 0
        oldest = self.requests[0]
        wait_until = oldest + self.window
        return max(0, wait_until - time.time())


class PerEndpointRateLimiter:
    """Configurable per-endpoint rate limiter"""
    
    # Default limits
    LIMITS = {
        # Auth endpoints - very strict
        "/api/auth/login": {"type": "sliding_window", "rate": 5, "window": 60},
        "/api/auth/signup": {"type": "sliding_window", "rate": 5, "window": 60},
        "/api/auth/forgot-password": {"type": "sliding_window", "rate": 3, "window": 60},
        
        # User management - moderate
        "/api/admin/users": {"type": "token_bucket", "rate": 20, "capacity": 30},
        "/api/user/": {"type": "token_bucket", "rate": 50, "capacity": 100},
        
        # Metrics and monitoring - relaxed
        "/api/metrics/": {"type": "token_bucket", "rate": 100, "capacity": 200},
        "/api/overview/": {"type": "token_bucket", "rate": 50, "capacity": 100},
        
        # General API - default
        "DEFAULT": {"type": "token_bucket", "rate": 100, "capacity": 200}
    }
    
    def __init__(self):
        self.limiters: Dict[str, Dict] = defaultdict(lambda: None)
    
    def get_limiter_config(self, endpoint: str) -> Dict:
        """Get rate limit config for endpoint"""
        # Check exact match first
        if endpoint in self.LIMITS:
            return self.LIMITS[endpoint]
        
        # Check prefix match
        for path_prefix in self.LIMITS:
            if path_prefix != "DEFAULT" and endpoint.startswith(path_prefix):
                return self.LIMITS[path_prefix]
        
        return self.LIMITS["DEFAULT"]
    
    def is_allowed(self, endpoint: str, identifier: str) -> Tuple[bool, Optional[float]]:
        """
        Check if request is allowed
        
        Args:
            endpoint: API endpoint path
            identifier: Client identifier (IP, user ID, etc)
        
        Returns:
            Tuple of (is_allowed, wait_seconds)
        """
        key = f"{endpoint}:{identifier}"
        config = self.get_limiter_config(endpoint)
        
        # Get or create limiter
        if key not in self.limiters or self.limiters[key] is None:
            if config["type"] == "token_bucket":
                self.limiters[key] = {
                    "limiter": TokenBucketLimiter(config["rate"], config["capacity"]),
                    "config": config
                }
            else:
                self.limiters[key] = {
                    "limiter": SlidingWindowLimiter(config["rate"], config["window"]),
                    "config": config
                }
        
        limiter_obj = self.limiters[key]["limiter"]
        allowed = limiter_obj.is_allowed()
        wait_time = limiter_obj.get_wait_time() if not allowed else 0
        
        return allowed, wait_time
    
    def get_stats(self, endpoint: str, identifier: str) -> Dict:
        """Get stats for endpoint:identifier pair"""
        key = f"{endpoint}:{identifier}"
        config = self.get_limiter_config(endpoint)
        
        if key in self.limiters and self.limiters[key]:
            limiter_obj = self.limiters[key]["limiter"]
            if config["type"] == "token_bucket":
                return {
                    "type": "token_bucket",
                    "tokens": round(limiter_obj.tokens, 2),
                    "capacity": limiter_obj.capacity,
                    "rate": limiter_obj.rate
                }
            else:
                return {
                    "type": "sliding_window",
                    "requests": len(limiter_obj.requests),
                    "limit": limiter_obj.rate,
                    "window": limiter_obj.window
                }
        
        return {"type": config["type"], "limit": config.get("rate", config.get("limit"))}


# Global rate limiter instance
rate_limiter = PerEndpointRateLimiter()
