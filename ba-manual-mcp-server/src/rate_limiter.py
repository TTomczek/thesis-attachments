import asyncio
import logging
from functools import wraps
from time import time
from collections import defaultdict
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.calls: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str, max_calls: int, time_window: int) -> Tuple[bool, float]:
        now = time()

        self.calls[key] = [call_time for call_time in self.calls[key]
                           if now - call_time < time_window]

        if len(self.calls[key]) < max_calls:
            self.calls[key].append(now)
            return True, 0

        oldest_call = min(self.calls[key])
        wait_time = time_window - (now - oldest_call)

        return False, wait_time


rate_limiter = RateLimiter()


def rate_limit(max_calls: int = 3, time_window: int = 60):

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}"
            allowed, wait_time = rate_limiter.is_allowed(key, max_calls, time_window)

            if not allowed:
                logger.warning(f"Rate limit exceeded for {key}")
                await asyncio.sleep(wait_time)

            return await func(*args, **kwargs)

        return wrapper

    return decorator