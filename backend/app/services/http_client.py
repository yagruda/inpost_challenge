import httpx
from typing import Optional

class HttpClientManager:
    client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls.client is None:
            # Configure pooling, limits, and timeouts for production
            limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
            timeout = httpx.Timeout(15.0, connect=5.0)
            cls.client = httpx.AsyncClient(limits=limits, timeout=timeout)
        return cls.client

    @classmethod
    async def close_client(cls):
        if cls.client:
            await cls.client.aclose()
            cls.client = None
