from fastapi import Depends, HTTPException, status
from redis import Redis

from app.core.config import settings
from app.core.redis import get_redis
from app.services.rate_limit_service import check_rate_limit
from app.api.v1.api_client_dependencies import get_current_api_client


def rate_limit_api_client(
    api_client=Depends(get_current_api_client),
    redis_client: Redis = Depends(get_redis),
):
    key = f"rate_limit:api_client:{api_client.id}"

    allowed, remaining = check_rate_limit(
        redis_client=redis_client,
        key=key,
        limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={
                "Retry-After": str(
                    settings.rate_limit_window_seconds
                ),
                "X-RateLimit-Remaining": "0",
            },
        )

    return {
        "remaining": remaining,
    }