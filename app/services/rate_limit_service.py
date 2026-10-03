from redis import Redis
from redis.exceptions import RedisError


def check_rate_limit(
    redis_client: Redis,
    key: str,
    limit: int,
    window_seconds: int,
) -> tuple[bool, int]:
    try:
        current_count = redis_client.incr(key)

        if current_count == 1:
            redis_client.expire(key, window_seconds)

        if current_count > limit:
            return False, 0

        remaining = max(limit - current_count, 0)

        return True, remaining

    except RedisError:
        # Fail open if Redis is temporarily unavailable.
        # The API remains available while rate limiting is unavailable.
        return True, limit