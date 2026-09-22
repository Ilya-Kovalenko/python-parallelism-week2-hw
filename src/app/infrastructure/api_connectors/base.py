import asyncio
import random
from typing import Mapping

import httpx


_RETRYABLE_STATUSES = {429, 503}


class RateLimiter:
    def __init__(self, requests: int, interval: float) -> None:
        self._semaphore = asyncio.Semaphore(requests)
        self._interval = interval

    async def acquire(self) -> None:
        await self._semaphore.acquire()
        asyncio.create_task(self._release_after_interval())

    async def _release_after_interval(self) -> None:
        await asyncio.sleep(self._interval + 0.05)
        self._semaphore.release()


class BaseHTTPConnector:
    def __init__(
        self,
        base_url: str,
        timeout: float,
        headers: Mapping[str, str] | None = None,
        *,
        rate_limit_requests: int | None = None,
        rate_limit_interval: float | None = None,
        retry_count: int = 3,
    ) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=timeout)
        self._rate_limiter = (
            RateLimiter(rate_limit_requests, rate_limit_interval)
            if rate_limit_requests is not None and rate_limit_interval is not None
            else None
        )
        self.retry_count = retry_count

    async def close_client(self):
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        url: str,
        *,
        retry: bool = False,
        **kwargs: object,
    ) -> httpx.Response:
        attempts = self.retry_count if retry else 1

        for attempt in range(1, attempts + 1):
            if self._rate_limiter:
                await self._rate_limiter.acquire()

            try:
                response = await self._client.request(method, url, **kwargs)
            except (httpx.NetworkError, httpx.TimeoutException):
                if attempt == attempts:
                    raise
            else:
                if response.status_code not in _RETRYABLE_STATUSES or attempt == attempts:
                    return response

            await self._exponential_backoff_sleep(attempt)

        raise RuntimeError("Request retry loop exited unexpectedly")

    @staticmethod
    async def _exponential_backoff_sleep(attempt: int) -> None:
        exponential_delay = 0.5 * 2 ** attempt
        jitter = random.uniform(0.1, 0.5)

        await asyncio.sleep(exponential_delay + jitter)
